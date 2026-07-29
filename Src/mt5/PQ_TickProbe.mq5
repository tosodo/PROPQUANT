//+------------------------------------------------------------------+
//| PQ_TickProbe.mq5 — PROPQUANT pre-grid tick validation (HARD GATE) |
//|                                                                  |
//| Monday's FIRST action. Pulls a ~1-hour slice of ticks and reports |
//| whether the feed can support the declared mechanism (order-flow   |
//| imbalance continuation), which needs buyer/seller classification. |
//|                                                                  |
//| INERT: CopyTicksRange + Print only. Writes NO strategy data,      |
//| places NO orders, touches NO account state. Run as a Script.      |
//|                                                                  |
//| See Research/PRE_GRID_VALIDATION.md for the decision rule. If     |
//| TICK_FLAG_BUY/SELL never appear, the mechanism is UNTESTABLE as   |
//| declared — stop, do not substitute a proxy classification.        |
//+------------------------------------------------------------------+
#property copyright "PROPQUANT"
#property version   "1.00"
#property script_show_inputs
#property strict

input string InpSymbol   = "XAUUSD";              // symbol to probe
input string InpFromUTC  = "2026.02.11 09:00:00"; // slice start (server time)
input int    InpMinutes  = 60;                    // slice length in minutes

//+------------------------------------------------------------------+
void OnStart()
{
   PrintFormat("[QA] INFO | server='%s' symbol=%s slice='%s' +%dmin",
               AccountInfoString(ACCOUNT_SERVER), InpSymbol, InpFromUTC, InpMinutes);

   if(!SymbolSelect(InpSymbol, true))
   {
      PrintFormat("[QA] FAIL | SymbolSelect(%s) failed (err %d)", InpSymbol, GetLastError());
      PrintFormat("[QA] ===== RESULT: GATE FAILED =====");
      return;
   }

   datetime from = StringToTime(InpFromUTC);
   datetime to   = from + InpMinutes * 60;

   MqlTick t[];
   // COPY_TICKS_ALL = every tick the base holds (quote updates AND trades, if any).
   int n = CopyTicksRange(InpSymbol, t, COPY_TICKS_ALL,
                          (ulong)from * 1000, (ulong)to * 1000);
   if(n <= 0)
   {
      PrintFormat("[QA] FAIL | CopyTicksRange returned %d (err %d) — no ticks in slice",
                  n, GetLastError());
      PrintFormat("[QA] ===== RESULT: GATE FAILED =====");
      return;
   }

   int digits = (int)SymbolInfoInteger(InpSymbol, SYMBOL_DIGITS);
   if(digits <= 0) digits = 2;
   double point = SymbolInfoDouble(InpSymbol, SYMBOL_POINT);

   //--- CHECK 1: bid/ask populated and sensible -----------------------
   int    bad_quote = 0;      // bid<=0, ask<=0, or ask<=bid
   double sp_sum = 0.0, sp_min = 1e18, sp_max = -1e18;
   int    sp_n = 0;
   for(int i=0; i<n; i++)
   {
      if(t[i].bid <= 0.0 || t[i].ask <= 0.0 || t[i].ask <= t[i].bid) { bad_quote++; continue; }
      double sp = t[i].ask - t[i].bid;
      sp_sum += sp; sp_n++;
      if(sp < sp_min) sp_min = sp;
      if(sp > sp_max) sp_max = sp;
   }
   double sp_avg = (sp_n > 0) ? sp_sum / sp_n : 0.0;

   //--- CHECK 2: flag histogram — the decisive one --------------------
   int f_bid=0, f_ask=0, f_last=0, f_vol=0, f_buy=0, f_sell=0, f_none=0;
   for(int i=0; i<n; i++)
   {
      uint f = (uint)t[i].flags;
      if(f == 0)                 f_none++;
      if((f & TICK_FLAG_BID)  != 0) f_bid++;
      if((f & TICK_FLAG_ASK)  != 0) f_ask++;
      if((f & TICK_FLAG_LAST) != 0) f_last++;
      if((f & TICK_FLAG_VOLUME)!= 0) f_vol++;
      if((f & TICK_FLAG_BUY)  != 0) f_buy++;
      if((f & TICK_FLAG_SELL) != 0) f_sell++;
   }

   //--- CHECK 3: parses cleanly (ordering + ms granularity) -----------
   int  back_steps = 0, dup_msc = 0, zero_msc = 0;
   for(int i=1; i<n; i++)
   {
      if(t[i].time_msc <  t[i-1].time_msc) back_steps++;
      if(t[i].time_msc == t[i-1].time_msc) dup_msc++;
      if(t[i].time_msc == 0)               zero_msc++;
   }

   //--- report --------------------------------------------------------
   PrintFormat("[QA] INFO | ticks=%d  digits=%d  point=%s", n, digits, DoubleToString(point, 8));

   bool c1 = (bad_quote * 100 <= n) && (sp_n > 0);   // <=1% malformed quotes
   PrintFormat("[QA] %s | CHECK 1 bid/ask | malformed=%d (%.2f%%)  spread avg=%s min=%s max=%s",
               c1 ? "PASS" : "FAIL", bad_quote, (n>0 ? 100.0*bad_quote/n : 0.0),
               DoubleToString(sp_avg, digits), DoubleToString(sp_min, digits),
               DoubleToString(sp_max, digits));

   bool c2 = (f_buy > 0 || f_sell > 0);
   PrintFormat("[QA] %s | CHECK 2 flags | BID=%d ASK=%d LAST=%d VOLUME=%d BUY=%d SELL=%d none=%d",
               c2 ? "PASS" : "FAIL", f_bid, f_ask, f_last, f_vol, f_buy, f_sell, f_none);
   if(!c2)
      PrintFormat("[QA] NOTE | no BUY/SELL flags — buyer/seller classification UNAVAILABLE. "
                  "Declared mechanism is UNTESTABLE as written. Do NOT substitute a proxy; "
                  "see Research/PRE_GRID_VALIDATION.md decision rule (i)/(ii).");

   bool c3 = (back_steps == 0) && (zero_msc == 0);
   PrintFormat("[QA] %s | CHECK 3 parse | backward_steps=%d duplicate_msc=%d zero_msc=%d",
               c3 ? "PASS" : "FAIL", back_steps, dup_msc, zero_msc);

   MqlDateTime d0, d1; TimeToStruct(t[0].time, d0); TimeToStruct(t[n-1].time, d1);
   PrintFormat("[QA] INFO | first=%04d.%02d.%02d %02d:%02d:%02d  last=%04d.%02d.%02d %02d:%02d:%02d",
               d0.year,d0.mon,d0.day,d0.hour,d0.min,d0.sec,
               d1.year,d1.mon,d1.day,d1.hour,d1.min,d1.sec);

   PrintFormat("[QA] ===== RESULT: GATE %s =====", (c1 && c2 && c3) ? "PASSED" : "FAILED");
}
//+------------------------------------------------------------------+
