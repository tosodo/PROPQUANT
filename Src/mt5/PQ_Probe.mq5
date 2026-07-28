//+------------------------------------------------------------------+
//| PQ_Probe.mq5 — diagnostic: is history reachable headless?        |
//| Inert. Prints connection/history state and tries a TINY CopyRates.|
//+------------------------------------------------------------------+
#property version "1.00"
#property strict

void OnStart()
{
   int passed=0, failed=0;
   bool connected = (bool)TerminalInfoInteger(TERMINAL_CONNECTED);
   long login     = AccountInfoInteger(ACCOUNT_LOGIN);
   PrintFormat("[QA] INFO | connected=%s server='%s' login=%I64d build=%d",
               connected?"YES":"NO", AccountInfoString(ACCOUNT_SERVER),
               login, (int)TerminalInfoInteger(TERMINAL_BUILD));

   string sym = "EURUSD";
   SymbolSelect(sym, true);
   long barsH1 = Bars(sym, PERIOD_H1);
   PrintFormat("[QA] INFO | Bars(%s,H1)=%I64d  SERIES_BARS_COUNT=%I64d",
               sym, barsH1, SeriesInfoInteger(sym, PERIOD_H1, SERIES_BARS_COUNT));

   // Tiny bounded request — last 10 bars only. Should be instant if the local
   // base is usable without a live sync.
   MqlRates r[];
   ArraySetAsSeries(r, true);
   int n = CopyRates(sym, PERIOD_H1, 0, 10, r);
   if(n > 0)
   {
      MqlDateTime d; TimeToStruct(r[0].time, d);
      PrintFormat("[QA] PASS | tiny CopyRates ok | got=%d newest=%04d.%02d.%02d %02d:%02d close=%s",
                  n, d.year,d.mon,d.day,d.hour,d.min, DoubleToString(r[0].close,5));
      passed++;
   }
   else
   {
      PrintFormat("[QA] FAIL | tiny CopyRates returned %d (err %d)", n, GetLastError());
      failed++;
   }
   PrintFormat("[QA] ===== RESULT: %d passed, %d failed =====", passed, failed);
}
//+------------------------------------------------------------------+
