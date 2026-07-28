//+------------------------------------------------------------------+
//| PQ_ExportBars.mq5 — PROPQUANT Gate 0 data export                 |
//|                                                                  |
//| Dumps OHLCV bar history to CSV for the PROPQUANT validation      |
//| funnel. INERT: reads local history + writes CSV files only.      |
//| Places NO orders, touches NO account state. Run as a Script.     |
//|                                                                  |
//| Output: MQL5/Files/PQ_<SYMBOL>_<TF>.csv, tab-separated, in the   |
//| same raw MT5-export column layout the Gate 0 validator expects:  |
//|   <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>
//+------------------------------------------------------------------+
#property copyright "PROPQUANT"
#property version   "1.00"
#property script_show_inputs
#property strict

// Which series to export. EURUSD + XAUUSD first (the deep-history pair).
input string InpSymbols = "EURUSD,XAUUSD";   // comma-separated
input int    InpMaxBars = 2000000;           // request cap; returns what exists

void ExportOne(const string sym, const ENUM_TIMEFRAMES tf, const string tfname,
               int &passed, int &failed)
{
   if(!SymbolSelect(sym, true))
   {
      PrintFormat("[QA] FAIL | EXPORT %s %s | SymbolSelect failed (err %d)", sym, tfname, GetLastError());
      failed++; return;
   }

   // Ask for exactly what's already in the local base. Requesting MORE than
   // exists while the terminal is CONNECTED makes MT5 try to download extra
   // history from the server and block on that round-trip — so size the request
   // to Bars() (the on-disk count), never an arbitrary huge cap.
   long avail = 0;
   for(int attempt=0; attempt<50 && avail<=0; attempt++) { avail = Bars(sym, tf); if(avail<=0) Sleep(200); }
   if(avail <= 0)
   {
      PrintFormat("[QA] FAIL | EXPORT %s %s | Bars()=0 (err %d)", sym, tfname, GetLastError());
      failed++; return;
   }
   int want = (int)MathMin(avail, (long)InpMaxBars);

   MqlRates r[];
   ArraySetAsSeries(r, false);                       // index 0 = oldest
   int n = CopyRates(sym, tf, 0, want, r);
   if(n <= 0)
   {
      PrintFormat("[QA] FAIL | EXPORT %s %s | CopyRates returned %d (avail=%I64d err %d)", sym, tfname, n, avail, GetLastError());
      failed++; return;
   }

   int digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
   if(digits <= 0) digits = 5;

   string fname = StringFormat("PQ_%s_%s.csv", sym, tfname);
   int h = FileOpen(fname, FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(h == INVALID_HANDLE)
   {
      PrintFormat("[QA] FAIL | EXPORT %s %s | FileOpen failed (err %d)", sym, tfname, GetLastError());
      failed++; return;
   }

   // Flush in chunks: accumulate a bounded buffer and write every CHUNK rows.
   // (Growing one huge string across all rows is O(n^2) and crawls; row-by-row
   //  FileWriteString is syscall-bound and slow. Chunked is O(n) and fast.)
   const int CHUNK = 1000;
   string buf = "<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\r\n";
   for(int i=0; i<n; i++)
   {
      MqlDateTime dt; TimeToStruct(r[i].time, dt);
      string dtstr = StringFormat("%04d.%02d.%02d\t%02d:%02d:%02d",
                                  dt.year, dt.mon, dt.day, dt.hour, dt.min, dt.sec);
      buf += dtstr
           + "\t" + DoubleToString(r[i].open,  digits)
           + "\t" + DoubleToString(r[i].high,  digits)
           + "\t" + DoubleToString(r[i].low,   digits)
           + "\t" + DoubleToString(r[i].close, digits)
           + "\t" + IntegerToString(r[i].tick_volume)
           + "\t" + IntegerToString(r[i].real_volume)
           + "\t" + IntegerToString((int)r[i].spread)
           + "\r\n";
      if((i % CHUNK) == (CHUNK-1)) { FileWriteString(h, buf); buf = ""; }
   }
   if(StringLen(buf) > 0) FileWriteString(h, buf);
   FileClose(h);

   MqlDateTime d0, d1; TimeToStruct(r[0].time, d0); TimeToStruct(r[n-1].time, d1);
   PrintFormat("[QA] PASS | EXPORT %s %s | bars=%d first=%04d.%02d.%02d last=%04d.%02d.%02d file=%s",
               sym, tfname, n, d0.year,d0.mon,d0.day, d1.year,d1.mon,d1.day, fname);
   passed++;
}

void OnStart()
{
   string server = AccountInfoString(ACCOUNT_SERVER);
   PrintFormat("[QA] INFO | terminal server='%s' data_path='%s'",
               server, TerminalInfoString(TERMINAL_DATA_PATH));

   string syms[];
   int ns = StringSplit(InpSymbols, ',', syms);

   ENUM_TIMEFRAMES tfs[] = {PERIOD_H1, PERIOD_H4};
   string          tfn[] = {"H1", "H4"};

   int passed=0, failed=0;
   for(int s=0; s<ns; s++)
   {
      string sym = syms[s];
      StringTrimLeft(sym); StringTrimRight(sym);
      if(StringLen(sym)==0) continue;
      for(int t=0; t<ArraySize(tfs); t++)
         ExportOne(sym, tfs[t], tfn[t], passed, failed);
   }

   PrintFormat("[QA] ===== RESULT: %d passed, %d failed =====", passed, failed);
}
//+------------------------------------------------------------------+
