//+------------------------------------------------------------------+
//|                                                DCA_MACD_Hedge.mq5|
//|                        Your Name / Your Company                  |
//+------------------------------------------------------------------+
#property copyright "GG The Ledgend"
#property link      "https://www.yourwebsite.com"
#property version   "1.40"
#property strict

#include <Trade\Trade.mqh>

//--- input parameters
input bool   InHedge                    = false;    // Should we hedge?
input double HedgeRiskPercent           = 5.0;  // Risk percentage for hedge positions
input double InHedgeATRMultiplier       = 30;    // Hedge Take Profit on ATR multipler InHedgeATRMultiplier
input double RiskPercent                = 1.0;      // Risk Percent Per Trade
input double InHighRiskWarning          = 5.0;      // Define % of risk is High Risk
input double DCAMultiplier              = 2.0;      // DCA Lot Size Multiplier
input double MaxDCAMultiple             = 4.0;      // Maximum DCA Multiple
input double RecoveryTarget             = 0.5;      // Recovery Target in Percent
input int    InNumbersOfTradeInDCA      = 5;        // Maximum number of DCA trades
input double InRecoveryProfit           = 50.0;     // Minimum recovery profit
input double InRiskPercentage           = 2.0;      // Maximum risk percentage for DCA
input double TakeProfitATRMultiplier    = 1.5;      // Take Profit ATR Multiplier

//--- ATR Parameters
input int    ATR_Period                 = 14;       // ATR Period
input double Initial_SL_ATR_Multiplier  = 2.0;      // Initial Stop Loss ATR Multiplier
input double DCA_SL_ATR_Multiplier      = 1.5;      // DCA Stop Loss ATR Multiplier
input double DCA_ATR_Multiplier         = 1.0;      // DCA Entry Distance ATR Multiplier
input double InTotalDCARiskPrecentage   = 30;      // Total Precentage of risk that DCA want to take.
input double Trailing_ATR_Multiplier    = 2.0;      // Trailing Stop ATR Multiplier
input double MinTrailingDistance        = 50;       // Minimum trailing stop distance (points)
input double InSIMULATEEXTREMEDROP      = 1000;     // Extreme Drop Strength (In term of price)
//--- Other Parameters
input int    MagicNumber                = 123456;   // Magic Number
input int    Slippage                   = 3;        // Slippage in Points
input int    RSIPeriod                  = 14;       // RSI Period
input int    RSIOverbought              = 70;       // RSI Overbought Level
input int    RSIOversold                = 30;       // RSI Oversold Level
input int    MACDFast                   = 12;       // MACD Fast EMA
input int    MACDSlow                   = 26;       // MACD Slow EMA
input int    MACDSignal                 = 9;        // MACD Signal Period


input double DistanceATRMulti           = 5;        // Assume each stop loss ATR distance
input double LotMultiplier              = 1;        // If your broker is using LOT and not mini

//--- global variables
CTrade ExtTrade;
int ExtSignalOpen  = 0;
int ExtSignalClose = 0;
string ExtDirection = "";
int ExtRSIHandle   = INVALID_HANDLE;
int ExtMACDHandle  = INVALID_HANDLE;
int ExtMACDH1Handle  = INVALID_HANDLE;
int ExtATRHandle   = INVALID_HANDLE;
int ExtMAFastHandle = INVALID_HANDLE;
int ExtMASlowHandle = INVALID_HANDLE;
datetime LastDCATime = 0;
double LastDCAPrice = 0;
bool DCAActivated = false;
bool ShortActivated = false;
bool EXtHedged = false;
bool HedgeIsNeeded = false;
bool HedgingNow = false;
double LastHedgePrice = 0;
bool IsTurnOnTrailing = false;
double total_deal_profit = 0;
bool HedgingCycleStarted = false;
bool IsSellStopHedge = false;
bool IsReduceJourneyStarted = false;
double InitialBalance =0;
double FirstHedgePrice = 0;
double LastShortPrice = 999999999;

// --- rescue functions
bool PortfolioTrailingActive = false;
double PortfolioTrailingPeak = 0.0;
double PortfolioTrailingStartEquity = 0.0;
double ReduceStartingBalance = 0.0;

//--- signal constants
#define SIGNAL_BUY   1
#define SIGNAL_SELL  2
#define CLOSE_LONG   1
#define CLOSE_SHORT  2

//--- DCA calculation result struct
struct DCACalculationResult
  {
   bool              isAchievable;
   double            requiredLots;
   double            targetPrice;
   double            takeProfitLevel;
   string            message;
   double            potentialLoss;
                     DCACalculationResult()
     {
      isAchievable = false;
      requiredLots = 0.0;
      targetPrice = 0.0;
      takeProfitLevel = 0.0;
      message = "";
     }
  };

struct SimulationResult
  {
   double            averagePrice;
   double            totalVolume;
   double            potentialProfitAtTP;
   double            potentialLossAtSL;
   double            takeProfitLevel;
                     SimulationResult()
     {
      averagePrice = 0.0;
      totalVolume = 0.0;
      potentialProfitAtTP = 0.0;
      potentialLossAtSL = 0.0;
      takeProfitLevel = 0.0;
     }
  };

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
  
   InitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   ExtTrade.SetExpertMagicNumber(MagicNumber);
   ExtTrade.SetDeviationInPoints(Slippage);
   ExtTrade.SetTypeFilling(ORDER_FILLING_FOK);
   ExtTrade.LogLevel(LOG_LEVEL_ALL);

   ExtRSIHandle  = iRSI(_Symbol, PERIOD_CURRENT, RSIPeriod, PRICE_CLOSE);
   ExtMACDHandle = iMACD(_Symbol, PERIOD_H1, MACDFast, MACDSlow, MACDSignal, PRICE_CLOSE);
   ExtMACDH1Handle = iMACD(_Symbol, PERIOD_H1, MACDFast, MACDSlow, MACDSignal, PRICE_CLOSE);
   ExtATRHandle  = iATR(_Symbol, PERIOD_CURRENT, ATR_Period);
   ExtMAFastHandle = iMA(_Symbol, PERIOD_H1, 9, 0, MODE_EMA, PRICE_CLOSE);
   ExtMASlowHandle = iMA(_Symbol, PERIOD_H1, 250, 0, MODE_EMA, PRICE_CLOSE);
   

   if(ExtMAFastHandle == INVALID_HANDLE || ExtMASlowHandle == INVALID_HANDLE || ExtRSIHandle == INVALID_HANDLE || ExtMACDHandle == INVALID_HANDLE || ExtATRHandle == INVALID_HANDLE ||ExtMACDH1Handle == INVALID_HANDLE)
     {
      //Print("Error creating indicators!");
      return INIT_FAILED;
     }

// Check if DCA is already active by counting positions
   if(CountPositions(ORDER_TYPE_BUY) > 1)
     {
      DCAActivated = true;
      //Print("DCA already active with ", CountPositions(ORDER_TYPE_BUY), " positions");
     }

   //Print("EA initialized successfully.");
   InitializeBalanceManagement();
   //potentialLossRisk =  CalculatePotentialLossWithCurrentPositions(5.0);
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   IndicatorRelease(ExtRSIHandle);
   IndicatorRelease(ExtMACDHandle);
   IndicatorRelease(ExtMACDH1Handle);
   IndicatorRelease(ExtATRHandle);
   //Print("EA deinitialized.");
  }

//+------------------------------------------------------------------+
//| Calculate potential loss with current positions                   |
//+------------------------------------------------------------------+
struct PotentialLossResult
  {
   double            potentialLoss;      // Absolute loss amount
   double            riskPercentage;     // Loss as percentage of balance
   double            averagePrice;       // Current average entry price
   double            totalVolume;        // Total volume of positions
   double            dropDistance;       // Price drop distance
   string            message;           // Detailed calculation message
  };


//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {

   if(HedgingCycleStarted && NoMoreLongPositions())
   {
       //Print("No more long positions. Closing all remaining positions.");
       CloseAllPositions();
       PortfolioTrailingActive = false; // Stop trailing if you were
   }
     
   static datetime lastBar;
   datetime currentBar = iTime(_Symbol, PERIOD_CURRENT, 0);
   if(currentBar == lastBar)
      return;
   lastBar = currentBar;
   CheckAndResetDCAStatus();
   
   if(IsReduceJourneyStarted)
    {
        CheckReduceSuccess();
    }

   if(PortfolioTrailingActive)
    {
        CheckPortfolioTrailingStop();
    }
   
   static datetime lastBalanceCheck = 0;
   datetime currentTime = TimeCurrent();
   PotentialLossResult potentialLossRisk =  CalculatePotentialLossWithCurrentPositions(5.0);
// Check balance status every hour
   if(currentTime - lastBalanceCheck >= PeriodSeconds(PERIOD_H1))
   {
      ////Print(GetBalanceStatus());
      
      CheckRiskLevels(potentialLossRisk);
      if(potentialLossRisk.riskPercentage > InHighRiskWarning)
      {
         Print("WARNING!!!!! PLEASE MANUAL OVERRIDE !!!!!!");
         if (!InHedge)
             return;
      }
      lastBalanceCheck = currentTime;
   }


// Check risk levels periodically
   static datetime lastCheck = 0;
//datetime currentTime = TimeCurrent();
//
//   if(currentTime - lastCheck >= 60)  // Check every minute
//     {
//
//      lastCheck = currentTime;
//     }

//--- Check for closing signals first
   
   double currentprice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(CheckCloseSignal() )
     {
      if(ExtSignalClose == CLOSE_LONG )
         ClosePositions(ORDER_TYPE_BUY);
      else
         if(ExtSignalClose == CLOSE_SHORT)
            ClosePositions(ORDER_TYPE_SELL);
     }

//--- Check for opening signals
   if(CheckOpenSignal())
     {
      if(ExtSignalOpen == SIGNAL_BUY)
         OpenPosition(ORDER_TYPE_BUY, Initial_SL_ATR_Multiplier);
      if(ExtSignalOpen == SIGNAL_SELL)
         OpenPosition(ORDER_TYPE_SELL, Initial_SL_ATR_Multiplier);
     }

// Check and update hedge SL if needed
   if(IsHedging())
     {
      //UpdateHedgeStopLoss();
         if (FirstHedgePrice < currentprice) {
            FirstHedgePrice = 0;
         }
     }

//--- Check for DCA opportunities
   DCACalculationResult dcaResult = CheckAndExecuteDCA();


   if(CheckHedgeSignal(dcaResult, potentialLossRisk))
     {
      if(ExtSignalOpen == SIGNAL_SELL) {
         EXtHedged = true;
         if (FirstHedgePrice == 0) {
            FirstHedgePrice = currentprice;
         }
         OpenHedgePosition(0,potentialLossRisk);    
      }

      //OpenPosition(ORDER_TYPE_SELL, dcaResult.targetPrice);

     }

//--- Trail stops by ATR
   TrailStopsByATR();
  }

//+------------------------------------------------------------------+
//| Check for opening signals                                        |
//+------------------------------------------------------------------+
bool CheckOpenSignal()
  {
   double rsi[], macdMain[], macdSignal[];
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(macdMain, true);
   ArraySetAsSeries(macdSignal, true);
   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   
   if(CopyBuffer(ExtRSIHandle, 0, 0, 5, rsi) != 5)
      return false;
   if(CopyBuffer(ExtMACDHandle, 0, 0, 2, macdMain) != 2)
      return false;
   if(CopyBuffer(ExtMACDHandle, 1, 0, 2, macdSignal) != 2)
      return false;

   
//--- Buy signal: RSI crosses up through oversold
   if(currentPrice > MASLOW() && !DCAActivated && !HedgingNow &&
      ((rsi[2] < RSIOversold && rsi[0] > RSIOversold) ||
       (rsi[1] < RSIOversold && rsi[0] > RSIOversold)))
     {
      //Print("BUY Signal - RSI Crossover Up - RSI[2]: ", rsi[2],", RSI[1]: ", rsi[1], " RSI[0]: ", rsi[0]);
      ExtSignalOpen = SIGNAL_BUY;
      ExtDirection = "Long";
      return true;
     }

   if(currentPrice < MASLOW() && !ShortActivated && currentPrice < LastShortPrice &&
      ((rsi[0] < RSIOverbought && rsi[2] > RSIOverbought) ||
       (rsi[0] < RSIOverbought && rsi[1] > RSIOverbought)))
     {
      //Print("Sell Signal - RSI Crossover Up - RSI[2]: ", rsi[2],", RSI[1]: ", rsi[1], " RSI[0]: ", rsi[0]);
      ExtSignalOpen = SIGNAL_SELL;
      ExtDirection = "Short";
      return false;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Check if hedge positions exist                                    |
//+------------------------------------------------------------------+
bool IsHedging()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;

      // Select the position to ensure it's still open
      if(!PositionSelectByTicket(ticket))
        {
         //Print("Failed to select position: ", GetLastError());
         continue;
        }

      // Check if position belongs to our EA
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(posType == POSITION_TYPE_SELL || IsSellStopHedge )
        {
         string comment = PositionGetString(POSITION_COMMENT);
         if(StringFind(comment, "Hedge@") >= 0 || IsSellStopHedge)
           {
            Print("IsSellStopHedge@",IsSellStopHedge, " Found active hedge position - Ticket: ", ticket,", Volume: ", PositionGetDouble(POSITION_VOLUME),", Open Price: ", PositionGetDouble(POSITION_PRICE_OPEN));
            return true;
           }
        }
     }
   HedgingNow = false;
   return false;
  }



//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool CheckHedgeSignal(DCACalculationResult &dcaCalculationResult, PotentialLossResult &potentialLossRisk)
  {

   bool shouldDCA = dcaCalculationResult.isAchievable;
   double potentialLoss = dcaCalculationResult.potentialLoss;
   PotentialLossResult risk = potentialLossRisk;
   double accountBalance = GetAvailableBalance();
   bool shouldHedge = MathAbs(risk.potentialLoss) > InTotalDCARiskPrecentage * accountBalance || 
                           risk.riskPercentage > InHighRiskWarning ;
   bool isHedgingNow = IsHedging();

//--- Sell signal: RSI crosses down through overbought and MACD < 0

   //Print(" Hedge enabled? ", InHedge, " Is Hedging Now? ", isHedgingNow,  " Should we Hedge now? " ,shouldHedge , "\n\r Hedging?", HedgingNow, " need? ",HedgeIsNeeded, " What is our Potential Loss?" , risk.potentialLoss);
   if(InHedge && shouldHedge && !isHedgingNow)
     {
      HedgingNow = true;
      ExtSignalOpen = SIGNAL_SELL;
      ExtDirection = "Short";
      return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Draw a red horizontal line at the MACD bottom                    |
//+------------------------------------------------------------------+
void DrawMACDBottomLine(int barIndex, double priceLevel)
  {
   string objName = "MACD_Bottom_Line_" + IntegerToString(barIndex) + "_" + TimeToString(TimeCurrent(), TIME_SECONDS);
   int startBar = barIndex - 20;
   int endBar   = barIndex + 20;

// Get times for start and end bars
   datetime timeStart = iTime(_Symbol, PERIOD_CURRENT, startBar);
   datetime timeEnd   = iTime(_Symbol, PERIOD_CURRENT, endBar);

// Create the trend line
   if(ObjectCreate(0, objName, OBJ_TREND, 0, timeStart, priceLevel, timeEnd, priceLevel))
     {
      ObjectSetInteger(0, objName, OBJPROP_COLOR, clrRed);
      ObjectSetInteger(0, objName, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, objName, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, objName, OBJPROP_RAY_LEFT, false);
      //Print("MACD bottom line drawn at price: ", priceLevel, " from bar ", startBar, " to ", endBar);
     }
   else
     {
      //Print("Failed to create MACD bottom line: ", GetLastError());
     }
  }


//+------------------------------------------------------------------+
//| Check for closing signals                                        |
//+------------------------------------------------------------------+
bool CheckCloseSignal()
  {
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double macdCurrent, signalCurrent, macdPrevious, signalPrevious;
   if(!GetMACDValues(0, macdCurrent, signalCurrent) ||
      !GetMACDValues(1, macdPrevious, signalPrevious))
     {
      return false;
     }

//--- Check for long position closure
   if(PositionExist(SIGNAL_BUY))
     {
      if(false && macdCurrent < signalCurrent && macdPrevious >= signalPrevious)
        {
         //Print("MACD bearish crossover - closing long positions");
         ExtSignalClose = CLOSE_LONG;
         ExtDirection = "Long";
         return true;
        }
     }

//--- Check for hedge position closure
   if(false && PositionExist(SIGNAL_SELL))
     {
      if((current_price > MASLOW()) && (true || IsMACDBottomForming()) || !DCAActivated)
        {
         //Print("MACD bottom forming - closing hedge positions");
         ExtSignalClose = CLOSE_SHORT;
         ExtDirection = "Short";
         HedgingNow = false;
         IsTurnOnTrailing = true;
         return true;
        }
     }

   return false;
  }

double MAFAST()
{
   double maBuffer[];
   ArraySetAsSeries(maBuffer,true);
   if (CopyBuffer(ExtMAFastHandle,0,0,1,maBuffer) == 1) {
         return maBuffer[0];
   }
   //Print("Failed to copy MA Fast buffer. Error: ", GetLastError());
   return -1;
}

double MASLOW()
{
   double maBuffer[];
   ArraySetAsSeries(maBuffer,true);
   if (CopyBuffer(ExtMASlowHandle,0,0,1,maBuffer) == 1) {
         return maBuffer[0];
   }
   //Print("Failed to copy MA Slow buffer. Error: ", GetLastError());
   return -1;
}


//+------------------------------------------------------------------+
//| Get MACD values for specified shift                              |
//+------------------------------------------------------------------+
bool GetMACDValues(int shift, double &macdValue, double &signalValue)
  {
   double macdBuffer[], signalBuffer[];
   ArraySetAsSeries(macdBuffer, true);
   ArraySetAsSeries(signalBuffer, true);

   if(CopyBuffer(ExtMACDHandle, 0, shift, 1, macdBuffer) != 1)
      return false;
   if(CopyBuffer(ExtMACDHandle, 1, shift, 1, signalBuffer) != 1)
      return false;

   macdValue = macdBuffer[0];
   signalValue = signalBuffer[0];
   return true;
  }
  


//+------------------------------------------------------------------+
//| Get MACD values for specified shift                              |
//+------------------------------------------------------------------+
bool GetMACDH1Values(int shift, double &macdValue, double &signalValue)
  {
   double macdBuffer[], signalBuffer[];
   ArraySetAsSeries(macdBuffer, true);
   ArraySetAsSeries(signalBuffer, true);

   if(CopyBuffer(ExtMACDH1Handle, 0, shift, 1, macdBuffer) != 1)
      return false;
   if(CopyBuffer(ExtMACDH1Handle, 1, shift, 1, signalBuffer) != 1)
      return false;

   macdValue = macdBuffer[0];
   signalValue = signalBuffer[0];
   return true;
  }


//+------------------------------------------------------------------+
//| Check if MACD is forming bottom                                  |
//+------------------------------------------------------------------+
bool IsMACDBottomForming()
{
   double macdCurrent, signalCurrent, macdPrevious, signalPrevious;
   
   //Print("=== Checking MACD Bottom Forming ===");
   
   if(!GetMACDH1Values(0, macdCurrent, signalCurrent))
   {
      //Print("Failed to get current MACD H1 values");
      int currentBar = GetCurrentBarIndex();
      double priceLevel = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      DrawMACDBottomLine(currentBar, priceLevel);
      return false;
   }
   //Print("Current MACD: ", macdCurrent, ", Signal: ", signalCurrent);
   
   if(!GetMACDH1Values(1, macdPrevious, signalPrevious))
   {
      //Print("Failed to get previous MACD H1 values");
      int currentBar = GetCurrentBarIndex();
      double priceLevel = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      DrawMACDBottomLine(currentBar, priceLevel);
      return false;
   }
   //Print("Previous MACD: ", macdPrevious, ", Signal: ", signalPrevious);

   // MACD is turning up from below zero
   bool isBottomForming = macdCurrent > macdPrevious && macdCurrent < 0;
   //Print("MACD Current > Previous: ", macdCurrent > macdPrevious);
   //Print("MACD Current > 0: ", macdCurrent > 0);
   //Print("Is Bottom Forming: ", isBottomForming);
   
   return isBottomForming;
}

//+------------------------------------------------------------------+
//| Get current bar index methods                                    |
//+------------------------------------------------------------------+

// Method 1: Using iBarShift
int GetCurrentBarIndex()
  {
   return Bars(_Symbol, PERIOD_CURRENT) - 1;
  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void OpenPosition(ENUM_ORDER_TYPE posType, double atrSLMultiplier)
  {
   double volume = CalculatePositionSize();
   double price = (posType == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                  : SymbolInfoDouble(_Symbol, SYMBOL_BID);

   double sl = CalculateATRStopLoss(posType, price, atrSLMultiplier);
   double tp = CalculateATRTakeProfit(posType, price);

  // if(posType == ORDER_TYPE_SELL)  // Hedge position
  //    sl = CalculateHedgeStopLoss(posType, price);

   string comment = (posType == ORDER_TYPE_BUY)
                    ? StringFormat("Long@%.5f", price)
                    : StringFormat("Hedge@%.5f", price);

   //Print("Opening ", (posType == ORDER_TYPE_SELL ? "hedge" : "initial"), " position:");
   //Print("Volume: ", volume);
   //Print("Price: ", price);
   //Print("Stop Loss: ", sl);

   if (sl < 0)
      sl =0;
   
   if (posType == ORDER_TYPE_SELL && LastShortPrice > price) {
        sl = LastShortPrice ;
   }  
   
   if(!ExtTrade.PositionOpen(_Symbol, posType, volume, price, sl, tp, comment))
     {
      //Print("Error opening position: ", GetLastError());
      return;
     }
   DCAActivated = true;
   LastDCAPrice = price;
   LastDCATime = TimeCurrent();
   if (posType == ORDER_TYPE_SELL) {
        LastShortPrice = price;
        ShortActivated = true;
   }
   //Print("Position opened successfully");
   
  }

void OpenHedgePosition(double offset, PotentialLossResult &potentialLossRisk )
{

   Print("╔════════════════════════════════════════════╗");
   Print("║ HEDGING POSITION STARTING                  ║");
   Print("╚════════════════════════════════════════════╝");
   DCAPositionInfo dcaInfo = CheckDCAPositions();
   if(!dcaInfo.hasDCAPositions)
   {
      //Print("No DCA positions found to hedge");
      return;
   }

   double atr[];
   ArraySetAsSeries(atr, true);
   double slDistance = 0;
   double takeProfit = 0;
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double volume = NormalizeDouble(GetTotalLongVolume() * 2, 2);  // Hedge full long position, rounded to 2 decimal places

   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
   {
      //Print("Failed to get ATR for stop loss.");
      return;
   }
   else
   {
      //slDistance = atr[0];
      slDistance = 20;
      //* InHedgeATRMultiplier;
   }

   // Calculate entry price based on offset
   double entryPrice;
   if(offset > 0.0)
   {
      // For sell stop order
      entryPrice = currentPrice - offset;
   }
   else
   {
      // For immediate execution
      entryPrice = currentPrice;
   }

   // Calculate stop loss and take profit
   double stopLoss = entryPrice + slDistance ;
   takeProfit = entryPrice - slDistance * 3;

   //Print("Opening hedge position:");
   Print("Current Price: ", currentPrice);
   Print("Entry Price: ", entryPrice);
   //Print("Stop Loss: ", stopLoss);
   //Print("Take Profit: ", takeProfit);
   Print("Volume: ", volume);
   Print("Offset: ", offset);
   PotentialLossResult risk = potentialLossRisk;
   // Check if we should proceed based on last hedge price
   if( risk.riskPercentage > InHighRiskWarning && ( LastHedgePrice > entryPrice || LastHedgePrice == 0))
   {
      if(offset > 0.0)
      {
         // Place sell stop order
         if(!ExtTrade.OrderOpen(
            _Symbol,                    // Symbol
            ORDER_TYPE_SELL_STOP,       // Order type
            volume,                     // Volume
            0,                          // Price (current)
            entryPrice,                 // Stop price (entry)
            stopLoss,                   // Stop loss
            takeProfit,                 // Take profit
            0,                         // Expiration
            "Hedge@" + DoubleToString(entryPrice, Digits()) // Comment
         ))
         {
            //Print("Error placing hedge sell stop order: ", GetLastError());
            return;
         }
         else
         {
            //Print("Hedge sell stop order placed successfully at ", entryPrice);
            HedgingCycleStarted = true;
            IsSellStopHedge = true;
            LastHedgePrice = entryPrice - MinTrailingDistance * point;
         }
      }
      else
      {
         // Immediate sell execution
         if(!ExtTrade.PositionOpen(
            _Symbol, 
            ORDER_TYPE_SELL, 
            volume, 
            entryPrice, 
            stopLoss, 
            takeProfit, 
            "Hedge@" + DoubleToString(entryPrice, Digits())
         ))
         {
            //Print("Error opening immediate hedge position: ", GetLastError());
            return;
         }
         else
         {
            //Print("Hedge position opened successfully at ", entryPrice);
            HedgingCycleStarted = true;
            LastHedgePrice = entryPrice - MinTrailingDistance * point;
            if (ReduceStartingBalance == 0)
                ReduceStartingBalance = AccountInfoDouble(ACCOUNT_EQUITY);
         }
      }
   }
   else
   {
      //Print("Skipping hedge position: Last hedge price (", LastHedgePrice, ") is lower than current entry price (", entryPrice, ")");
   }
}

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void old_v1_OpenHedgePosition(double offset = 0.0)
  {
   DCAPositionInfo dcaInfo = CheckDCAPositions();
   if(!dcaInfo.hasDCAPositions)
     {
      //Print("No DCA positions found to hedge");
      return;
     }

   double atr[];
   ArraySetAsSeries(atr, true);
   double slDistance = 0;
   double takeProfit = 0;


   double openPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for stop loss.");
      return;
     }
   else
     {

      slDistance = atr[0] * InHedgeATRMultiplier;
      takeProfit = openPrice - slDistance * 3;
     }

   double volume = GetTotalLongVolume();  // Hedge full long position
   double stopLoss = openPrice + 100;
   //CalculateHedgeStopLoss(ORDER_TYPE_SELL, openPrice);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

   //stopLoss = dcaInfo.averagePrice;
   
   stopLoss  = openPrice + 800;
   
   takeProfit = openPrice - 1000;
   //Print("Opening hedge position:");
   //Print("Price: ", openPrice);
   //Print("Stop Loss (DCA Target): ", stopLoss);
   //Print("Volume: ", dcaInfo.totalVolume);



// Verify the calculation before opening position
   //if(false && !VerifyHedgeStopLoss(openPrice, stopLoss, volume))
   //  {
   //   //Print("WARNING: Stop loss calculation verification failed!");
   //   return;  // Don't open position if verification fails
   //  }

// Proceed with position opening
   if(LastHedgePrice > openPrice || LastHedgePrice ==0)
      if(!ExtTrade.PositionOpen(_Symbol, ORDER_TYPE_SELL, volume, openPrice, 
      stopLoss, takeProfit, "Hedge@" + DoubleToString(openPrice, Digits())))
        {
         //Print("Error opening hedge position: ", GetLastError());
         return;
        }
      else
        {
         HedgingCycleStarted = true;
         LastHedgePrice = openPrice - MinTrailingDistance * point;
        }
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool VerifyHedgeStopLoss(double openPrice, double stopLoss, double volume)
  {
   double accountBalance = GetAvailableBalance();
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

// Calculate actual potential loss
   double priceDistance = MathAbs(stopLoss - openPrice);
   double pointDistance = priceDistance / point;
   double moneyPerPoint = tickValue * (point / tickSize);  // This gives us the correct money per point for ANY symbol
   double potentialLoss = pointDistance * moneyPerPoint * volume;
   double actualRiskPercent = (potentialLoss / accountBalance) * 100;

   //Print("--- Stop Loss Verification ---");
   //Print("Price Distance: ", priceDistance);
   //Print("Point Distance: ", pointDistance);
   //Print("Tick Value: ", tickValue);
   //Print("Tick Size: ", tickSize);
   //Print("Point: ", point);
   //Print("Money per Point: ", moneyPerPoint);
   //Print("Volume: ", volume);
   //Print("Potential Loss: ", potentialLoss);
   //Print("Actual Risk Percent: ", actualRiskPercent, "%");
   //Print("Target Risk Percent: ", HedgeRiskPercent, "%");

   return MathAbs(actualRiskPercent - HedgeRiskPercent) <= 0.1;
  }
//+------------------------------------------------------------------+
//| Open new position                                                |
//+------------------------------------------------------------------+
void old_v_1_OpenPosition(ENUM_ORDER_TYPE posType, double atrSLMultiplier)
  {
   double volume = old_v1_CalculatePositionSize();
   double price = (posType == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                  : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double sl = CalculateATRStopLoss(posType, price, atrSLMultiplier);
   double tp = CalculateATRTakeProfit(posType, price);

   //Print("Opening position: ", EnumToString(posType), " Volume: ", volume, " Price: ", price, " SL: ", sl, " TP: ", tp);

   if(!ExtTrade.PositionOpen(_Symbol, posType, volume, price, sl, tp))
     {
      //Print("Error opening position: ", GetLastError());
      return;
     }

   //Print("Position opened: ", EnumToString(posType), " Volume: ", volume);
  }

//+------------------------------------------------------------------+
//| Calculate position size based on risk and position type          |
//+------------------------------------------------------------------+
double CalculatePositionSize(bool isHedge = false)
  {
// Step 1: Get account and market information
   double accountBalance = GetAvailableBalance();
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double pointValue = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

// For hedge positions, return total volume of long positions
   if(isHedge)
     {
      double totalLongVolume = GetTotalLongVolume();
      //Print("--- Hedge Position Size Calculation ---");
      //Print("Total Long Volume to Hedge: ", totalLongVolume);
      return totalLongVolume;
     }

// Step 2: Get current ATR value for risk calculation
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for position sizing. Using default risk distance.");
      // Fallback to a default calculation if ATR is not available
      double riskAmount = accountBalance * RiskPercent / 100.0;
      double volume = NormalizeDouble(riskAmount / (100 * tickValue), 2);
      volume = MathFloor(volume / lotStep) * lotStep;
      volume = MathMax(minVolume, MathMin(volume, maxVolume));
      volume = volume * DCAMultiplier;
      return volume;
     }
   double atrValue = atr[0];

// Step 3: Calculate maximum potential position size after DCA
   double maxDCAFactor = 0.0;
   for(int i = 0; i < InNumbersOfTradeInDCA; i++)
     {
      maxDCAFactor += MathPow(DCAMultiplier, i);
     }

// Step 4: Calculate maximum potential loss based on ATR and stop loss distance
   double slDistance = atrValue * DistanceATRMulti;// Assume fix atr multiple not yet Initial_SL_ATR_Multiplier;
   double maxRiskPerLot = slDistance * tickValue / tickSize;

// Step 5: Calculate the maximum risk amount based on account balance and risk percentage
   double maxRiskAmount = accountBalance  * RiskPercent / 100.0;

// Step 6: Calculate the initial position size
   double initialVolume = maxRiskAmount / (maxRiskPerLot * maxDCAFactor);

// Step 7: Normalize and apply constraints
   double volume = NormalizeDouble(initialVolume, 2);
   volume = MathFloor(volume / lotStep) * lotStep;
   volume = MathMax(minVolume, MathMin(volume, maxVolume));

// //Print detailed calculation information
   Print("--- Initial Position Size Calculation Details ---");
   Print("Account Balance: ", accountBalance);
   Print("Risk Percent: ", RiskPercent, "%");
   Print("Maximum Risk Amount: ", maxRiskAmount);
   Print("Current ATR Value: ", atrValue);
   Print("Stop Loss Distance (ATR * Multiplier): ", slDistance);
   Print("Risk Per 1.0 Lot: ", maxRiskPerLot);
   Print("Maximum DCA Factor: ", maxDCAFactor);
   Print("Calculated Initial Volume: ", initialVolume);
   Print("Normalized Volume: ", volume);
   Print("Tick Value: ", tickValue);
   Print("Tick Size: ", tickSize);
   Print("Point Value: ", pointValue);
   Print("Lot Step: ", lotStep);
   Print("Min Volume: ", minVolume);
   Print("Max Volume: ", maxVolume);

   return volume * LotMultiplier;
  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double CalculateHedgeStopLoss(ENUM_ORDER_TYPE orderType, double openPrice)
  {
   double accountBalance = GetAvailableBalance();
   double maxLoss = accountBalance * HedgeRiskPercent / 100.0;
   double totalVolume = GetTotalLongVolume();
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

// Calculate how many points movement equals one tick
   double pointsPerTick = tickSize / point;

// Calculate how much money we lose per point of movement
   double moneyPerPoint = (tickValue / tickSize)  * totalVolume ;

// Calculate required distance in points to reach maxLoss
   double slDistancePoints = maxLoss / moneyPerPoint;

// Convert points to price distance
   double slDistance = slDistancePoints ;
   double sl = (orderType == ORDER_TYPE_SELL) ? openPrice + slDistance : openPrice - slDistance;
   //Print("--- Hedge Stop Loss Calculation ---");
   //Print("Account Balance: ", accountBalance);
   //Print("The point and tick size: ", point, " tick Size: ", tickSize);
   //Print("Hedge Risk Percent: ", HedgeRiskPercent, "%");
   //Print("Maximum Allowed Loss: ", maxLoss);
   //Print("Total Volume: ", totalVolume);
   //Print("Tick Value: ", tickValue);
   //Print("Tick Size: ", tickSize);
   //Print("Point: ", point);
   //Print("Points per Tick: ", pointsPerTick);
   //Print("Money per Point: ", moneyPerPoint);
   //Print("SL Distance in Points: ", slDistancePoints);
   //Print("SL Distance in Price: ", slDistance);
   //Print("Open Price: ", openPrice);
   //Print("SL Price: ", sl);

// Verify the calculation
   double potentialLoss = slDistance * moneyPerPoint;
   double riskPercent = (potentialLoss / accountBalance) * 100;
   //Print("Verification:");
   //Print("Potential Loss at SL: ", potentialLoss);
   //Print("Actual Risk Percent: ", riskPercent, "%");


// Add safety check
   if(MathAbs(riskPercent - HedgeRiskPercent) > 0.1)  // If calculated risk is off by more than 0.1%
     {
      //Print("WARNING: Calculated risk percent differs significantly from target risk percent!");
     }
//LastHedgePrice = sl - MinTrailingDistance * point;
   if(orderType == ORDER_TYPE_SELL)
      return openPrice + slDistance;
   else
      return openPrice - slDistance;
  }


//+------------------------------------------------------------------+
//| Calculate position size based on risk                            |
//+------------------------------------------------------------------+
double old_v1_CalculatePositionSize()
  {
// Step 1: Get account and market information
   double accountBalance = GetAvailableBalance();
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double pointValue = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

// Step 2: Get current ATR value for risk calculation
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for position sizing. Using default risk distance.");
      // Fallback to a default calculation if ATR is not available
      double riskAmount = accountBalance * RiskPercent / 100.0;
      double volume = NormalizeDouble(riskAmount / (100 * tickValue), 2);
      volume = MathFloor(volume / lotStep) * lotStep;
      volume = MathMax(minVolume, MathMin(volume, maxVolume));
      volume = volume * DCAMultiplier;
      return volume;
     }
   double atrValue = atr[0];

// Step 3: Calculate maximum potential position size after DCA
// Initial position + potential DCA positions with multiplier
   double maxDCAFactor = 0.0;
   for(int i = 0; i < InNumbersOfTradeInDCA; i++)
     {
      maxDCAFactor += MathPow(DCAMultiplier, i);
     }

// Step 4: Calculate maximum potential loss based on ATR and stop loss distance
   double slDistance = atrValue * Initial_SL_ATR_Multiplier; // Distance in price
   double maxRiskPerLot = slDistance * tickValue / tickSize; // Risk per 1.0 lot

// Step 5: Calculate the maximum risk amount based on account balance and risk percentage
   double maxRiskAmount = accountBalance * RiskPercent / 100.0;

// Step 6: Calculate the initial position size that keeps total risk within limits
// even after potential DCA operations
   double initialVolume = maxRiskAmount / (maxRiskPerLot * maxDCAFactor);

// Step 7: Normalize and apply constraints
   double volume = NormalizeDouble(initialVolume, 2);
   volume = MathFloor(volume / lotStep) * lotStep;
   volume = MathMax(minVolume, MathMin(volume, maxVolume));

// //Print detailed calculation information for debugging
   //Print("--- Position Size Calculation Details ---");
   //Print("Account Balance: ", accountBalance);
   //Print("Risk Percent: ", RiskPercent, "%");
   //Print("Maximum Risk Amount: ", maxRiskAmount);
   //Print("Current ATR Value: ", atrValue);
   //Print("Stop Loss Distance (ATR * Multiplier): ", slDistance);
   //Print("Risk Per 1.0 Lot: ", maxRiskPerLot);
   //Print("Maximum DCA Factor (sum of multipliers): ", maxDCAFactor);
   //Print("Calculated Initial Volume: ", initialVolume);
   //Print("Normalized Volume: ", volume);
   //Print("Tick Value: ", tickValue);
   //Print("Tick Size: ", tickSize);
   //Print("Point Value: ", pointValue);
   //Print("Lot Step: ", lotStep);
   //Print("Min Volume: ", minVolume);
   //Print("Max Volume: ", maxVolume);

   return volume;
  }

//+------------------------------------------------------------------+
//| Calculate ATR-based stop loss                                    |
//+------------------------------------------------------------------+
double CalculateATRStopLoss(ENUM_ORDER_TYPE posType, double openPrice, double atrMultiplier)
  {
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for stop loss.");
      return 0;
     }
   double atrValue = atr[0];
   double distance = atrValue * atrMultiplier;

   if(posType == ORDER_TYPE_BUY)
      return openPrice - distance;
   else
      return openPrice + distance;
  }

//+------------------------------------------------------------------+
//| Calculate ATR-based take profit                                  |
//+------------------------------------------------------------------+
double CalculateATRTakeProfit(ENUM_ORDER_TYPE posType, double openPrice)
  {
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for take profit.");
      return 0;
     }
   double atrValue = atr[0];
   double distance = atrValue * TakeProfitATRMultiplier;

   if(posType == ORDER_TYPE_BUY)
      return openPrice + distance;
   else
      return openPrice - distance;
  }

//+------------------------------------------------------------------+
//| Trail stops by ATR                                               |
//+------------------------------------------------------------------+
void TrailStopsByATR()
  {
// If no positions, exit
   if(CountPositions(ORDER_TYPE_BUY) == 0)
      return;

   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for trailing stop.");
      return;
     }
   double atrValue = atr[0];
   double trailDistance = MathMax(atrValue * Trailing_ATR_Multiplier, MinTrailingDistance * _Point) ;

// Get current market prices
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

// If DCA is active, check if average price is below current bid by 5 ATR
   if(DCAActivated || CountPositions(ORDER_TYPE_BUY) > 1)
     {
      double avgPrice = CalculateAveragePrice();
      double profitThreshold = 5 * atrValue; // 5 ATR profit threshold

      // Only start trailing if we have sufficient profit (5 ATR)
      if(bid > avgPrice + profitThreshold || IsTurnOnTrailing)
        {
         //Print("Average price (", avgPrice, ") is below current bid (", bid, ") by 5 ATR (", profitThreshold, "). Starting trailing stop.");

         // Before trailing, increase TP to 3 times its current value for all positions
         IncreaseAllPositionsTP(10.0);

         TrailAllPositionsTogether(trailDistance);
        }
      else
        {
         ////Print("Not trailing yet. Average price: ", avgPrice, ", Current bid: ", bid,
         //    ", Required profit (5 ATR): ", profitThreshold,
         //  ", Current profit: ", bid - avgPrice);
        }
      return;
     }

// Standard trailing for single positions - only if price has moved in our favor by 5 ATR
   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_ORDER_TYPE posType = (ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);
      double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double profitThreshold = 1 * atrValue; // 5 ATR profit threshold

      if(posType == ORDER_TYPE_BUY)
        {
         // Only trail if we have sufficient profit (5 ATR)
         if(bid > entryPrice + profitThreshold)
           {
            // Increase TP to 3 times its current value before trailing starts
            double newTP = currentTP;
            if(currentTP > 0)
              {
               double tpDistance = currentTP - entryPrice;
               newTP = entryPrice + (tpDistance * 3.0);
               //Print("Increasing TP from ", currentTP, " to ", newTP, " (3x) as trailing begins");
              }

            double newSL = bid - trailDistance;
            if((currentSL == 0.0 || newSL > currentSL) && newSL < bid)
              {
               //Print("Trailing BUY SL to: ", newSL);
               ExtTrade.PositionModify(ticket, newSL, newTP);
              }
           }
         else
           {
            //Print("Not trailing single position yet. Entry price: ", entryPrice,", Current bid: ", bid,", Required profit (5 ATR): ", profitThreshold, ", Current profit: ", bid - entryPrice);
           }
        }
      else
         if(posType == ORDER_TYPE_SELL)
           {
            // Only trail if we have sufficient profit (5 ATR)
            if(ask < entryPrice - profitThreshold)
              {
               // Increase TP to 3 times its current value before trailing starts
               double newTP = currentTP;
               if(currentTP > 0)
                 {
                  double tpDistance = entryPrice - currentTP;
                  newTP = entryPrice - (tpDistance * 3.0);
                  //Print("Increasing TP from ", currentTP, " to ", newTP, " (3x) as trailing begins");
                 }

               double newSL = ask + trailDistance;
               if((currentSL == 0.0 || newSL < currentSL) && newSL > ask)
                 {
                  //Print("Trailing SELL SL to: ", newSL);
                  ExtTrade.PositionModify(ticket, newSL, newTP);
                  EXtHedged = false;
                 }
              }
            else
              {
               //Print("Not trailing single position yet. Entry price: ", entryPrice,", Current ask: ", ask, ", Required profit (5 ATR): ", profitThreshold,", Current profit: ", entryPrice - ask);
              }
           }
     }
  }

//+------------------------------------------------------------------+
//| Increase TP for all positions by a multiplier                    |
//+------------------------------------------------------------------+
void IncreaseAllPositionsTP(double multiplier)
  {
   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_ORDER_TYPE posType = (ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);
      double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);

      // Only modify if there's a valid TP
      if(currentTP > 0)
        {
         double newTP;
         if(posType == ORDER_TYPE_BUY)
           {
            double tpDistance = currentTP - entryPrice;
            newTP = entryPrice + (tpDistance * multiplier);
           }
         else // SELL
           {
            double tpDistance = entryPrice - currentTP;
            newTP = entryPrice - (tpDistance * multiplier);
           }

         //Print("Increasing TP for ticket #", ticket, " from ", currentTP, " to ", newTP, " (", multiplier, "x)");
         ExtTrade.PositionModify(ticket, currentSL, newTP);
        }
     }
  }

//+------------------------------------------------------------------+
//| Trail stops by ATR                                               |
//+------------------------------------------------------------------+
void old_v_2_TrailStopsByATR()
  {
// If no positions, exit
   if(CountPositions(ORDER_TYPE_BUY) == 0)
      return;

   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for trailing stop.");
      return;
     }
   double atrValue = atr[0];
   double trailDistance = MathMax(atrValue * Trailing_ATR_Multiplier, MinTrailingDistance * _Point);

// Get current market prices
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

// If DCA is active, check if average price is below current bid by 5 ATR
   if(DCAActivated || CountPositions(ORDER_TYPE_BUY) > 1)
     {
      double avgPrice = CalculateAveragePrice();
      double profitThreshold = 5 * atrValue; // 5 ATR profit threshold

      // Only start trailing if we have sufficient profit (5 ATR)
      if(bid > avgPrice + profitThreshold)
        {
         //Print("Average price (", avgPrice, ") is below current bid (", bid, ") by 5 ATR (", profitThreshold, "). Starting trailing stop.");
         TrailAllPositionsTogether(trailDistance);
        }
      else
        {
         //Print("Not trailing yet. Average price: ", avgPrice, ", Current bid: ", bid, ", Required profit (5 ATR): ", profitThreshold,", Current profit: ", bid - avgPrice);
        }
      return;
     }

// Standard trailing for single positions - only if price has moved in our favor by 5 ATR
   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_ORDER_TYPE posType = (ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);
      double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double profitThreshold = 5 * atrValue; // 5 ATR profit threshold

      if(posType == ORDER_TYPE_BUY)
        {
         // Only trail if we have sufficient profit (5 ATR)
         if(bid > entryPrice + profitThreshold)
           {
            double newSL = bid - trailDistance;
            if((currentSL == 0.0 || newSL > currentSL) && newSL < bid)
              {
               //Print("Trailing BUY SL to: ", newSL);
               ExtTrade.PositionModify(ticket, newSL, currentTP);
              }
           }
         else
           {
            //Print("Not trailing single position yet. Entry price: ", entryPrice, ", Current bid: ", bid,", Required profit (5 ATR): ", profitThreshold,", Current profit: ", bid - entryPrice);
           }
        }
      else
         if(posType == ORDER_TYPE_SELL)
           {
            // Only trail if we have sufficient profit (5 ATR)
            if(ask < entryPrice - profitThreshold)
              {
               double newSL = ask + trailDistance;
               if((currentSL == 0.0 || newSL < currentSL) && newSL > ask)
                 {
                  //Print("Trailing SELL SL to: ", newSL);
                  ExtTrade.PositionModify(ticket, newSL, currentTP);
                 }
              }
            else
              {
               //Print("Not trailing single position yet. Entry price: ", entryPrice,", Current ask: ", ask,", Required profit (5 ATR): ", profitThreshold,", Current profit: ", entryPrice - ask);
              }
           }
     }
  }
//+------------------------------------------------------------------+
//| Trail stops by ATR                                               |
//+------------------------------------------------------------------+
void old_v_1_TrailStopsByATR()
  {
// If no positions, exit
   if(CountPositions(ORDER_TYPE_BUY) == 0)
      return;

   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for trailing stop.");
      return;
     }
   double atrValue = atr[0];
   double trailDistance = MathMax(atrValue * Trailing_ATR_Multiplier, MinTrailingDistance * _Point);

// If DCA is active, trail all positions together based on average price
   if(DCAActivated || CountPositions(ORDER_TYPE_BUY) > 1)
     {
      TrailAllPositionsTogether(trailDistance);
      return;
     }

// Standard trailing for single positions
   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_ORDER_TYPE posType = (ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double entryPrice = PositionGetDouble(POSITION_PRICE_OPEN);

      if(posType == ORDER_TYPE_BUY)
        {
         double newSL = bid - trailDistance;
         if((currentSL == 0.0 || newSL > currentSL) && newSL < bid && bid > entryPrice)
           {
            //Print("Trailing BUY SL to: ", newSL);
            ExtTrade.PositionModify(ticket, newSL, currentTP);
           }
        }
      else
         if(posType == ORDER_TYPE_SELL)
           {
            double newSL = ask + trailDistance;
            if((currentSL == 0.0 || newSL < currentSL) && newSL > ask)
              {
               //Print("Trailing SELL SL to: ", newSL);
               ExtTrade.PositionModify(ticket, newSL, currentTP);
              }
           }
     }
  }

//+------------------------------------------------------------------+
//| Trail all positions together based on average price              |
//+------------------------------------------------------------------+
void TrailAllPositionsTogether(double trailDistance)
  {
   double averagePrice = CalculateAveragePrice();
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

// Only trail if price is above average entry
   if(bid <= averagePrice)
      return;

// Calculate new stop loss based on current price and trail distance
   double newSL = bid - trailDistance;

// Get current common stop loss (if exists)
   double currentCommonSL = GetCommonStopLoss();

// Only update if new SL is higher than current common SL
   if(currentCommonSL == 0.0 || newSL > currentCommonSL)
     {
      //Print("DCA Mode: Trailing all positions SL to: ", newSL, " (Average Price: ", averagePrice, ")");

      // Update all positions with the same SL
      for(int i = 0; i < PositionsTotal(); i++)
        {
         ulong ticket = PositionGetTicket(i);
         if(ticket <= 0)
            continue;
         if(PositionGetString(POSITION_SYMBOL) != _Symbol)
            continue;
         if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
            continue;
         if(PositionGetInteger(POSITION_TYPE) != ORDER_TYPE_BUY)
            continue;

         double currentTP = PositionGetDouble(POSITION_TP);
         ExtTrade.PositionModify(ticket, newSL, currentTP);
        }
     }
  }

//+------------------------------------------------------------------+
//| Get common stop loss level if all positions have the same SL     |
//+------------------------------------------------------------------+
double GetCommonStopLoss()
  {
   double commonSL = 0.0;
   bool firstPosition = true;

   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != ORDER_TYPE_BUY)
         continue;

      double currentSL = PositionGetDouble(POSITION_SL);

      if(firstPosition)
        {
         commonSL = currentSL;
         firstPosition = false;
        }
      else
         if(MathAbs(commonSL - currentSL) > _Point)
           {
            // If any position has a different SL, return 0
            return 0.0;
           }
     }

   return commonSL;
  }

//+------------------------------------------------------------------+
//| Check if DCA trade count exceeded limit                           |
//+------------------------------------------------------------------+
bool CheckIfDCATradeNumberExceeded()
  {
   int dcaCount = 0;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
        {
         string comment = PositionGetString(POSITION_COMMENT);
         if(StringFind(comment, "DCA") >= 0)
           {
            dcaCount++;
           }
        }
     }

   //Print("--- DCA Count Check ---");
   //Print("Current DCA Count: ", dcaCount);
   //Print("Maximum Allowed: ", InNumbersOfTradeInDCA);
   //Print("Can Add More DCA: ", (dcaCount < InNumbersOfTradeInDCA));

   return dcaCount >= InNumbersOfTradeInDCA;
  }

//+------------------------------------------------------------------+
//| Check and execute DCA if needed                                  |
//+------------------------------------------------------------------+
DCACalculationResult CheckAndExecuteDCA()
  {
   DCACalculationResult result;
   PotentialLossResult potentialLossRisk =  CalculatePotentialLossWithCurrentPositions(5.0);
   if(!PositionExist(SIGNAL_BUY))
      return result;
      
   //Print("DCA Checking...");
   if( (CheckIfDCATradeNumberExceeded() || HedgingCycleStarted ))
     {
      return result;
     }
    //Print("Calculate Profit Checking...");
   double currentProfit = CalculateTotalProfit();
   if(currentProfit < 0  && !HedgingNow )
     {
      //Print("Ready for DCA Checking...");
   
      // Check if enough time has passed since last DCA
      if(TimeCurrent() - LastDCATime < 360) // 6 mins cool down 1 hour cooldown @3600
        {
  
         return result;
        }
      DCACalculationResult dcaResult = CalculateDCAForRecovery();
      Print("---- DCA Calculation: ----- ", dcaResult.message);
      if(dcaResult.isAchievable && dcaResult.requiredLots > 0.0)
        {
         double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double sl = CalculateATRStopLoss(ORDER_TYPE_BUY, price, DCA_SL_ATR_Multiplier);
         Print("Opening DCA position: Volume: ", dcaResult.requiredLots, " Price: ", price, " SL: ", sl, " TP: ", dcaResult.takeProfitLevel);
         if(sl < 0)
            sl=0;

         double lot_size = NormalizeDouble(dcaResult.requiredLots,2);
         if(!ExtTrade.PositionOpen(_Symbol, ORDER_TYPE_BUY, lot_size,
                                   price, sl, dcaResult.takeProfitLevel, "DCA Trading @" + price))
         {
            Print("Error opening DCA position: ", GetLastError());
            return result;
         }
         else {
         
            if (HedgingCycleStarted) {
               // TODO: 
               // Close Hedge Position 
               // Open new Hedge Position with Sell Stop Order
               // Fix all the parameters. 
               // Close existing hedge positions
               CloseAllHedgePositions();
   
               // Calculate ATR for hedge offset
               double atr[];
               ArraySetAsSeries(atr, true);
               if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
               {
                  //Print("Failed to get ATR for hedge offset calculation.");
               }
               else
               {
                  // Place new hedge sell stop order at ATR-based distance
                  double hedgeOffset = atr[0] * InHedgeATRMultiplier;
                  //Print("Setting up new hedge position with offset: ", hedgeOffset);
                  //OpenHedgePosition(hedgeOffset);  // This will place a sell stop order
               }         
            
            }
 
         }

         //Print("DCA position opened: Volume: ", dcaResult.requiredLots);

         // Update all existing positions with the new take profit level and stop loss
         UpdateAllPositionsTPandSL(dcaResult.takeProfitLevel, sl);

         // Mark DCA as activated
         DCAActivated = true;
         LastDCATime = TimeCurrent();
         LastDCAPrice = price;
        }
      else
         if(!dcaResult.isAchievable)
           {
            //Print("DCA not achievable: ", dcaResult.message);
           }

      return dcaResult;
     }
   return result;
  }

//+------------------------------------------------------------------+
//| Update all positions with the same take profit and stop loss     |
//+------------------------------------------------------------------+
void UpdateAllPositionsTPandSL(double takeProfitLevel, double stopLossLevel)
  {
   for(int i = 0; i < PositionsTotal(); i++)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != ORDER_TYPE_BUY)
         continue;

      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);

      if(currentTP != takeProfitLevel || currentSL != stopLossLevel)
        {
         //Print("Updating position #", ticket, " TP from ", currentTP, " to ", takeProfitLevel,  " and SL from ", currentSL, " to ", stopLossLevel);
         if(!ExtTrade.PositionModify(ticket, stopLossLevel, takeProfitLevel))
           {
            //Print("Error updating position TP/SL: ", GetLastError());
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Calculate total profit of open positions                         |
//+------------------------------------------------------------------+
double CalculateTotalProfit()
  {
   double totalProfit = 0.0;
   for(int i = 0; i < PositionsTotal(); i++)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      totalProfit += PositionGetDouble(POSITION_PROFIT);
     }
   //Print("Total Profit: " , totalProfit);
   return totalProfit;
  }

//+------------------------------------------------------------------+
//| Calculate average price of open positions                        |
//+------------------------------------------------------------------+
double CalculateAveragePrice()
  {
   double totalVolume = 0.0;
   double weightedPrice = 0.0;

   for(int i = 0; i < PositionsTotal(); i++)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != ORDER_TYPE_BUY)
         continue;

      double posVolume = PositionGetDouble(POSITION_VOLUME);
      double posPrice = PositionGetDouble(POSITION_PRICE_OPEN);

      totalVolume += posVolume;
      weightedPrice += posPrice * posVolume;
     }

   return (totalVolume > 0) ? weightedPrice / totalVolume : 0;
  }

//+------------------------------------------------------------------+
//| Get total volume of long positions                               |
//+------------------------------------------------------------------+
double GetTotalLongVolume()
  {
   double totalVolume = 0.0;
   for(int i = 0; i < PositionsTotal(); i++)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_TYPE) == ORDER_TYPE_BUY)
        {
         totalVolume += PositionGetDouble(POSITION_VOLUME);
        }
     }
////Print("Total Long Volume: ", totalVolume);
   return totalVolume;
  }

//+------------------------------------------------------------------+
//| Count number of positions by type                                |
//+------------------------------------------------------------------+
int CountPositions(ENUM_ORDER_TYPE posType)
  {
   int count = 0;
   for(int i = 0; i < PositionsTotal(); i++)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      if(PositionGetInteger(POSITION_TYPE) == posType)
        {
         count++;
        }
     }
   return count;
  }

//+------------------------------------------------------------------+
//| Simulate DCA position                                            |
//+------------------------------------------------------------------+
SimulationResult SimulateDCAPosition(double currentPrice, double slLevel, int additionalPositions)
  {
   SimulationResult result;

   double currentTotalVolume = GetTotalLongVolume();
   double currentAveragePrice = CalculateAveragePrice();
   double newPositionVolume = currentTotalVolume * DCAMultiplier * additionalPositions;
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

// Calculate ATR for take profit
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      //Print("Failed to get ATR for simulation.");
      return result;
     }
   double atrValue = atr[0];

   double totalValue = (currentTotalVolume * currentAveragePrice) + (newPositionVolume * currentPrice);
   double newTotalVolume = currentTotalVolume + newPositionVolume;
   double newAveragePrice = totalValue / newTotalVolume;

// Calculate take profit level based on new average price
   double tpDistance = atrValue * TakeProfitATRMultiplier;
   double tpLevel = newAveragePrice + tpDistance;

   result.averagePrice = newAveragePrice;
   result.totalVolume = newTotalVolume;
   result.takeProfitLevel = tpLevel;
   result.potentialProfitAtTP = (tpLevel - newAveragePrice) * newTotalVolume * tickValue / tickSize;
   result.potentialLossAtSL = (slLevel - newAveragePrice) * newTotalVolume * tickValue / tickSize;

   //Print("DCA Simulation Plan (Position ", additionalPositions, "):");
   //Print("Current State:");
   //Print("  Current Total Volume: ", currentTotalVolume);
   //Print("  Current Average Price: ", currentAveragePrice);
   //Print("  Current Market Price: ", currentPrice);
   //Print("  Tick Value: ", tickValue);
   //Print("  Tick Size: ", tickSize);

   //Print("New Position Calculation:");
   //Print("  New Position Volume: ", newPositionVolume);
   //Print("  Total Value: ", totalValue);
   //Print("  New Total Volume: ", newTotalVolume);
   //Print("  New Average Price: ", newAveragePrice);

   //Print("Profit/Loss Projections:");
   //Print("  Take Profit Level: ", tpLevel);
   //Print("  Stop Loss Level: ", slLevel);
   //Print("  Potential Profit at TP: ", result.potentialProfitAtTP);
   //Print("  Potential Loss at SL: ", result.potentialLossAtSL);

   //Print("Risk Analysis:");
   //Print("  Distance to TP: ", tpLevel - newAveragePrice);
   //Print("  Distance to SL: ", slLevel - newAveragePrice);
   //Print("  Risk/Reward Ratio: ", MathAbs(result.potentialProfitAtTP/result.potentialLossAtSL));

   return result;
  }


//+------------------------------------------------------------------+
//| Calculate DCA parameters for recovery                            |
//+------------------------------------------------------------------+
DCACalculationResult CalculateDCAForRecovery()
  {
   DCACalculationResult result;
   result.requiredLots = 0;
   result.isAchievable = false;

   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double point_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double accountBalance = GetAvailableBalance();
   double averagePrice = CalculateAveragePrice();

   double currentAveragePrice = CalculateAveragePrice();
   double currentTotalVolume = GetTotalLongVolume();
   int currentPositions = CountPositions(ORDER_TYPE_BUY);

   if(currentPositions == 0)
     {
      result.message = "No open positions found";
      return result;
     }

// ATR-based DCA entry distance
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      result.message = "Failed to get ATR value for DCA.";
      return result;
     }
   double atrValue = atr[0];
   double dcaDistance = DCA_ATR_Multiplier * averagePrice;
   //Print("DEBUG: DCA Distance" , dcaDistance);
   // Only DCA if price has moved down enough
   if(LastDCAPrice > 0 && currentPrice > LastDCAPrice - dcaDistance)
     {
      double targetDCAPrice = LastDCAPrice - dcaDistance;
      result.message = StringFormat(
                          "Price hasn't moved enough for DCA (ATR-based). Last DCA Price: %.5f,\n\r Current Price: %.5f, " +
                          "Required Distance: %.5f, Target Price for DCA: %.5f",
                          LastDCAPrice, currentPrice, dcaDistance, targetDCAPrice);
                          
      // Example usage:
      DrawOrangeLine("Target DCA", targetDCAPrice);
      return result;
     }

// Calculate stop loss level for new position
   double slLevel = currentPrice - (atrValue * DCA_SL_ATR_Multiplier);

// Calculate required positions
   for(int additionalPos = 1; additionalPos <= InNumbersOfTradeInDCA; additionalPos++)
     {
      SimulationResult sim = SimulateDCAPosition(currentPrice, slLevel, additionalPos);

      double potentialProfit = sim.potentialProfitAtTP;
      double potentialLoss = MathAbs(sim.potentialLossAtSL);
      //Print("Simulating add pos ", additionalPos);
      if(potentialProfit >= InRecoveryProfit)
        {
         //TODO:  how to calculate potential loss
         if(true || potentialLoss <= accountBalance * InRiskPercentage / 100)
           {
            result.requiredLots = sim.totalVolume - currentTotalVolume;
            result.targetPrice = sim.averagePrice;
            result.takeProfitLevel = sim.takeProfitLevel;
            result.isAchievable = true;

            result.message = StringFormat(
                                "Recovery plan calculated with %d additional positions\n" +
                                "Lot Size: %.5f\n" +"Average Entry: %.5f\n" +
                                "Total Volume: %.2f\n" +
                                "Take Profit Level: %.5f\n" +
                                "Stop Loss Level: %.5f\n" +
                                "Potential Profit: %.2f\n" +
                                "Max Loss: %.2f\n" +
                                "Risk Percentage: %.2f%%",
                                additionalPos,
                                result.requiredLots,
                                result.targetPrice,
                                sim.totalVolume,
                                result.takeProfitLevel,
                                slLevel,
                                potentialProfit,
                                potentialLoss,
                                (potentialLoss / accountBalance) * 100
                             );
            result.potentialLoss = potentialLoss;
            return result;
           }
        }
     }

   result.message = StringFormat(
                       "Recovery target of %.2f not achievable within %d additional positions\n" +
                       "or risk constraints of %.2f%%",
                       InRecoveryProfit,
                       InNumbersOfTradeInDCA,
                       InRiskPercentage
                    );

   return result;
  }

//+------------------------------------------------------------------+
//| Check if all positions are closed and reset DCA status if needed |
//+------------------------------------------------------------------+
void CheckAndResetDCAStatus()
  {
// Check if there are no open buy positions
   if(CountPositions(ORDER_TYPE_BUY) == 0 && CountPositions(ORDER_TYPE_SELL) == 0)
     {
      // Only //Print message if DCA was previously activated
      if(DCAActivated || LastDCATime > 0 || LastDCAPrice > 0)
        {
         //Print("All positions closed, resetting DCA status");

         // Reset all DCA-related variables
         DCAActivated = false;
         ShortActivated = false;
         LastShortPrice = 9999999;
         LastDCATime = 0;
         LastDCAPrice = 0;
         HedgingNow = false;
         LastHedgePrice =0 ;
         IsTurnOnTrailing = false;
         total_deal_profit = 0;
         HedgingCycleStarted = false;
         IsReduceJourneyStarted = false;
         ReduceStartingBalance =0.0;
        }
     }

  }

//+------------------------------------------------------------------+
//| Close all positions of specified type                            |
//+------------------------------------------------------------------+
void ClosePositions(ENUM_ORDER_TYPE posType)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != posType)
         continue;

      if(!ExtTrade.PositionClose(PositionGetTicket(i)))
        {
         //Print("Error closing position: ", GetLastError());
        }
      else
        {
         //Print("Closed position: ", PositionGetTicket(i));
        }
     }

// Reset DCA status if all buy positions are closed
   if(posType == ORDER_TYPE_BUY && CountPositions(ORDER_TYPE_BUY) == 0)
     {
      DCAActivated = false;
      LastDCATime = 0;
      LastDCAPrice = 0;
      //Print("All buy positions closed, DCA status reset");
     }
  }

//+------------------------------------------------------------------+
//| Check if position exists                                         |
//+------------------------------------------------------------------+
bool PositionExist(int signal)
  {
   for(int i = 0; i < PositionsTotal(); i++)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      ENUM_ORDER_TYPE posType = (ENUM_ORDER_TYPE)PositionGetInteger(POSITION_TYPE);
      if((signal == SIGNAL_BUY && posType == ORDER_TYPE_BUY) ||
         (signal == SIGNAL_SELL && posType == ORDER_TYPE_SELL))
        {
         return true;
        }
     }
   return false;
  }




//+------------------------------------------------------------------+
//| Calculate potential loss including pending sell stop orders        |
//+------------------------------------------------------------------+
PotentialLossResult old_CalculatePotentialLossWithCurrentPositions(double atrMultiplier = 5.0)
{
   PotentialLossResult result;

   // Get market conditions
   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double avaiableAccountBalanceForTrade = GetAvailableBalance();
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

   // Get ATR value
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
   {
      result.message = "Failed to get ATR value";
      return result;
   }

   result.dropDistance = InSIMULATEEXTREMEDROP;
   
   // Calculate current positions loss potential
   result.averagePrice = CalculateAveragePrice();
   result.totalVolume = GetTotalLongVolume();
   
   double totalPotentialLoss = 0;
   double combinedVolume = result.totalVolume;
   double pointsLoss = 0;
   // Calculate potential loss for current positions
   if(result.totalVolume > 0)
   {
      double worstPrice = currentPrice - result.dropDistance;
      pointsLoss = (result.averagePrice - worstPrice) / tickSize;
      totalPotentialLoss = pointsLoss * result.totalVolume * (tickValue / tickSize);
      
      if (pointsLoss <=0 || worstPrice < 0) {
            totalPotentialLoss = 0;
      }
   }

   // Get pending sell stop orders
   double sellStopLoss = 0;
   double sellStopVolume = 0;
   double sellStopEntryPrice = 0;
   
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong ticket = OrderGetTicket(i);
      if(OrderSelect(ticket))
      {
         if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
         if(OrderGetInteger(ORDER_MAGIC) != MagicNumber) continue;
         if(OrderGetInteger(ORDER_TYPE) != ORDER_TYPE_SELL_STOP) continue;
         
         double orderVolume = OrderGetDouble(ORDER_VOLUME_CURRENT);
         double orderEntry = OrderGetDouble(ORDER_PRICE_OPEN);
         double orderSL = OrderGetDouble(ORDER_SL);
         
         // Calculate potential loss for this sell stop order
         double orderRiskPoints = (orderSL - orderEntry) / tickSize;
         double orderPotentialLoss = orderRiskPoints * orderVolume * tickValue;
         
         // Calculate additional loss from current price to entry
         double entryPoints = (currentPrice - orderEntry) / tickSize;
         double entryLoss = entryPoints * orderVolume * tickValue;
         
         sellStopLoss += (orderPotentialLoss + entryLoss);
         sellStopVolume += orderVolume;
         
         // Store the highest entry price of sell stops
         if(orderEntry > sellStopEntryPrice) sellStopEntryPrice = orderEntry;
      }
   }

   // Combine all potential losses
   result.potentialLoss = totalPotentialLoss + sellStopLoss;
   result.totalVolume = combinedVolume + sellStopVolume;
   
   // Calculate risk percentage
   //result.riskPercentage = (1-((currentEquity - result.potentialLoss) / accountBalance)) * 100;
   result.riskPercentage = (1-((currentEquity - result.potentialLoss) / InitialBalance)) * 100;
   //Print ("Current Equity ", currentEquity, " potentialLoss " , result.potentialLoss);

   //Print("--- Potential Loss Calculation Details ---");
   //Print("Current Positions Loss: ", totalPotentialLoss);
   //Print("Sell Stop Orders Loss: ", sellStopLoss);
   //Print("Current Positions Volume: ", combinedVolume);
   //Print("Sell Stop Orders Volume: ", sellStopVolume);
   //Print("Combined Potential Loss: ", result.potentialLoss);
   
   // Create detailed message
   result.message = StringFormat(
      " - - - - Potential Loss Analysis - - - -\n" +
      "Current Price: %.5f\n" +
      "Average Entry: %.5f\n" +
      "Current Positions Volume: %.2f\n" +
      "Sell Stop Volume: %.2f\n" +
      "Total Volume: %.2f\n" +
      "ATR Value: %.5f\n" +
      "Drop Distance: %.5f\n" + "Point Loss: %.5f\n" +
      "Current Positions Loss: %.2f\n" +
      "Sell Stop Orders Loss: %.2f\n" +
      "Total Potential Loss: %.2f\n" +
      "Risk Percentage: %.2f%%\n" +
      "Avaiable Balance For Trading: %.2f\n" +
      "Initial Balance: %.2f\n"+
      "Tick Size: %.5f\n"+
      "Tick Value: %.2f\n",
      currentPrice,
      result.averagePrice,
      combinedVolume,
      sellStopVolume,
      result.totalVolume,
      atr[0],
      result.dropDistance,
      pointsLoss, 
      totalPotentialLoss,
      sellStopLoss,
      result.potentialLoss,
      result.riskPercentage,
      avaiableAccountBalanceForTrade,
      InitialBalance,
      tickSize,
      tickValue
   );

   //Print(result.message);
   return result;
}
PotentialLossResult CalculatePotentialLossWithCurrentPositions(double atrMultiplier = 5.0)
{
   PotentialLossResult result;

   // Get market conditions
   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double avaiableAccountBalanceForTrade = GetAvailableBalance();
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);

   // Get ATR value
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
   {
      result.message = "Failed to get ATR value";
      return result;
   }

   result.dropDistance = atrMultiplier * atr[0];

   // Calculate total long and short volume and their weighted average prices
   double totalLongVolume = 0, totalShortVolume = 0;
   double weightedLongPrice = 0, weightedShortPrice = 0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(PositionSelectByTicket(ticket) && PositionGetString(POSITION_SYMBOL) == _Symbol)
      {
         double posVolume = PositionGetDouble(POSITION_VOLUME);
         double posPrice = PositionGetDouble(POSITION_PRICE_OPEN);
         int posType = PositionGetInteger(POSITION_TYPE);

         if(posType == POSITION_TYPE_BUY)
         {
            weightedLongPrice += posPrice * posVolume;
            totalLongVolume += posVolume;
         }
         else if(posType == POSITION_TYPE_SELL)
         {
            weightedShortPrice += posPrice * posVolume;
            totalShortVolume += posVolume;
         }
      }
   }

   double avgLongPrice = (totalLongVolume > 0) ? weightedLongPrice / totalLongVolume : 0;
   double avgShortPrice = (totalShortVolume > 0) ? weightedShortPrice / totalShortVolume : 0;

   // Net volume and average price for net position
   double netVolume = totalLongVolume - totalShortVolume;
   double avgNetPrice = 0;
   if(netVolume > 0)
      avgNetPrice = avgLongPrice;
   else if(netVolume < 0)
      avgNetPrice = avgShortPrice;
   else
      avgNetPrice = currentPrice; // Flat, no exposure

   // Calculate net loss if price drops
   double worstPriceDrop = currentPrice - result.dropDistance;
   double netLossIfDrop = 0;
   if(netVolume > 0) // Net long
      netLossIfDrop = netVolume * (avgNetPrice - worstPriceDrop) * contractSize * 10;
   else if(netVolume < 0) // Net short
      netLossIfDrop = 0; // Shorts gain if price drops

   // Calculate net loss if price rises
   double worstPriceRise = currentPrice + result.dropDistance;
   double netLossIfRise = 0;
   if(netVolume < 0) // Net short
      netLossIfRise = -netVolume * (worstPriceRise - avgNetPrice) * contractSize;
   else if(netVolume > 0) // Net long
      netLossIfRise = 0; // Longs gain if price rises

   // Get pending sell stop orders (as before)
   double sellStopLoss = 0;
   double sellStopVolume = 0;

   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong ticket = OrderGetTicket(i);
      if(OrderSelect(ticket))
      {
         if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
         if(OrderGetInteger(ORDER_MAGIC) != MagicNumber) continue;
         if(OrderGetInteger(ORDER_TYPE) != ORDER_TYPE_SELL_STOP) continue;

         double orderVolume = OrderGetDouble(ORDER_VOLUME_CURRENT);
         double orderEntry = OrderGetDouble(ORDER_PRICE_OPEN);
         double orderSL = OrderGetDouble(ORDER_SL);

         // Calculate potential loss for this sell stop order
         double orderRiskPoints = (orderSL - orderEntry) / tickSize;
         double orderPotentialLoss = orderRiskPoints * orderVolume * tickValue;

         // Calculate additional loss from current price to entry
         double entryPoints = (currentPrice - orderEntry) / tickSize;
         double entryLoss = entryPoints * orderVolume * tickValue;

         sellStopLoss += (orderPotentialLoss + entryLoss);
         sellStopVolume += orderVolume;
      }
   }

   // The worst-case scenario is the maximum of the two net losses
   double potentialLoss = MathMax(netLossIfDrop, netLossIfRise) + sellStopLoss;

   result.potentialLoss = potentialLoss;
   result.totalVolume = MathAbs(netVolume) + sellStopVolume;
   result.averagePrice = avgNetPrice;

   // Calculate risk percentage
   result.riskPercentage = (1-((currentEquity - result.potentialLoss) / InitialBalance)) * 100;
   //Print ("Current Equity ", currentEquity, " potentialLoss " , result.potentialLoss);

   //Print("--- Potential Loss Calculation Details ---");
   //Print("Net Loss If Drop: ", netLossIfDrop);
   //Print("Net Loss If Rise: ", netLossIfRise);
   //Print("Sell Stop Orders Loss: ", sellStopLoss);
   //Print("Net Volume: ", netVolume);
   //Print("Sell Stop Orders Volume: ", sellStopVolume);
   //Print("Combined Potential Loss: ", result.potentialLoss);

   // Create detailed message
   result.message = StringFormat(
      " - - - - Potential Loss Analysis - - - -\n" +
      "Current Price: %.5f\n" +
      "Avg Long Entry: %.5f\n" +
      "Avg Short Entry: %.5f\n" +
      "Net Volume: %.2f\n" +
      "Sell Stop Volume: %.2f\n" +
      "Total Volume: %.2f\n" +
      "ATR Value: %.5f\n" +
      "Drop Distance: %.5f\n" + "Current Equity: %.2f\n" +
      "Net Loss If Drop: %.2f\n" +
      "Net Loss If Rise: %.2f\n" +
      "Sell Stop Orders Loss: %.2f\n" +
      "Total Potential Loss: %.2f\n" +
      "Risk Percentage: %.2f%%\n" +
      "Avaiable Balance For Trading: %.2f\n" +
      "Initial Balance: %.2f\n"+
      "Tick Size: %.5f\n"+
      "Tick Value: %.2f\n",
      currentPrice,
      avgLongPrice,
      avgShortPrice,
      netVolume,
      sellStopVolume,
      MathAbs(netVolume) + sellStopVolume,
      atr[0],
      result.dropDistance,
      currentEquity,
      netLossIfDrop,
      netLossIfRise,
      sellStopLoss,
      result.potentialLoss,
      result.riskPercentage,
      avaiableAccountBalanceForTrade,
      InitialBalance,
      tickSize,
      tickValue
   );

   Print(result.message);
   return result;
}

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
PotentialLossResult old_v2_CalculatePotentialLossWithCurrentPositions(double atrMultiplier = 5.0)
  {
   PotentialLossResult result;

// Get current market conditions
   double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double accountBalance = GetAvailableBalance();
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

// Get ATR value
   double atr[];
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
     {
      result.message = "Failed to get ATR value";
      return result;
     }

// Calculate drop distance based on ATR
   double atrValue = atr[0];
   
   result.dropDistance = InSIMULATEEXTREMEDROP;
   // atrValue * atrMultiplier;

// Get current positions info
   result.averagePrice = CalculateAveragePrice();
   result.totalVolume = GetTotalLongVolume();

   if(result.totalVolume == 0)
     {
      result.message = "No open positions";
      return result;
     }

// Calculate potential loss
   double worstPrice = currentPrice - result.dropDistance;
   double pointsLoss = (result.averagePrice - worstPrice) / tickSize;
   result.potentialLoss = (pointsLoss * result.totalVolume * tickValue) ;
   
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   //Print("--- Potential Loss Calculation Details ---");
   //Print("Tick Value: ", tickValue);
   //Print("Tick Size: ", tickSize);
   //Print("Point: ", point);
   //Print("Points Loss: ", pointsLoss);
   //Print("Total Volume: ", result.totalVolume);
   
   // Break down the calculation
   //double rawCalculation = pointsLoss * result.totalVolume;
   ////Print("Step 1 - Points Loss * Total Volume: ", rawCalculation);
   
   //double tickValueAdjustment = rawCalculation * tickValue;
   ////Print("Step 2 - Multiply by Tick Value: ", tickValueAdjustment);
   
   //result.potentialLoss = tickValueAdjustment / tickSize;
   ////Print("Step 3 - Final Result (divided by Tick Size): ", result.potentialLoss);
   
   // Additional verification
   double verificationCalc = (pointsLoss * point) * (result.totalVolume * 100000) * (tickValue / tickSize);
   ////Print("Verification calculation: ", verificationCalc);

   // Current Account Balance minus potential loss. 
   result.riskPercentage = (1-((currentEquity - result.potentialLoss) / accountBalance)) * 100;
   
// Create detailed message
   result.message = StringFormat(
                       " - - - - Potential Loss Analysis - - - -\n" +
                       "Current Price: %.5f\n" +
                       "Average Entry: %.5f\n" +
                       "Total Volume: %.2f\n" +
                       "ATR Value: %.5f\n" +
                       "Drop Distance (ATR * %.1f): %.5f\n" +
                       "Worst Price: %.5f\n" +
                       "Points Loss: %.5f\n" +
                       "Potential Loss: %.2f\n" +
                       "Risk Percentage: %.2f%%\n" +
                       "Account Balance: %.2f\n" +
                       "Initial Balance: %.2f\n"+
                       "Ticket Size: %.2f\n"+
                       "Ticket Value: %.2f\n" ,
                       currentPrice,
                       result.averagePrice,
                       result.totalVolume,
                       atrValue,
                       atrMultiplier,
                       result.dropDistance,
                       worstPrice,
                       pointsLoss,
                       result.potentialLoss,
                       result.riskPercentage,
                       accountBalance, 
                       InitialBalance,
                       tickSize,
                       tickValue
                  
                    );

   //Print(result.message);

   return result;
  }

// In your decision-making logic
PotentialLossResult CheckRiskLevels(PotentialLossResult &potentialLossRisk)
  {
   PotentialLossResult risk = potentialLossRisk;

   if(risk.totalVolume > 0)  // If we have positions
     {

      ////Print(risk.message);

      // Example risk thresholds
      if(risk.riskPercentage > InHighRiskWarning)  // High risk
        {
         //Print("Current Risk Analysis:");
         //Print("WARNING: High risk level detected: ", risk.riskPercentage, "%");
         //Print(risk.message);
         // Consider hedging or closing positions
         HedgeIsNeeded = true;
        }
      else
         if(risk.riskPercentage > 2.0)  // Medium risk
           {
            //Print("CAUTION: Elevated risk level: ", risk.riskPercentage, "%");
            // Consider partial hedging or tightening stops

           }
         else
            if(risk.riskPercentage < 2.0)  // Medium risk
              {

               if(HedgeIsNeeded)
                  //Print("Info: Dropping risk level: ", risk.riskPercentage, "%");
                  // Consider partial hedging or tightening stops
                  HedgeIsNeeded = false;
                  IsHedging();
                  //|| potentialLossRisk.riskPercentage < InRiskPercentage)
              }



     }
   return risk;
  }

//+------------------------------------------------------------------+
//| Structure to hold DCA position information                        |
//+------------------------------------------------------------------+
struct DCAPositionInfo
  {
   bool              hasDCAPositions;
   double            averagePrice;
   double            totalVolume;
   double            targetPrice;    // TP target for DCA positions
   int               positionCount;
   string            message;
  };

//+------------------------------------------------------------------+
//| Check for active DCA positions                                    |
//+------------------------------------------------------------------+
DCAPositionInfo CheckDCAPositions()
  {
   DCAPositionInfo info;
   info.hasDCAPositions = false;
   info.averagePrice = 0;
   info.totalVolume = 0;
   info.targetPrice = 0;
   info.positionCount = 0;

   double weightedPrice = 0;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
        {
         string comment = PositionGetString(POSITION_COMMENT);
         // Check if it's a DCA position
         if(StringFind(comment, "DCA") >= 0)
           {
            double posVolume = PositionGetDouble(POSITION_VOLUME);
            double posPrice = PositionGetDouble(POSITION_PRICE_OPEN);
            double posTP = PositionGetDouble(POSITION_TP);

            info.hasDCAPositions = true;
            info.totalVolume += posVolume;
            weightedPrice += posPrice * posVolume;
            info.positionCount++;

            // Store the TP of the last DCA position as target
            if(posTP > 0)
               info.targetPrice = posTP;
           }
        }
     }

   if(info.hasDCAPositions && info.totalVolume > 0)
     {
      info.averagePrice = weightedPrice / info.totalVolume;

      info.message = StringFormat(
                        "DCA Positions Found:\n" +
                        "Count: %d\n" +
                        "Total Volume: %.2f\n" +
                        "Average Price: %.5f\n" +
                        "Target Price: %.5f",
                        info.positionCount,
                        info.totalVolume,
                        info.averagePrice,
                        info.targetPrice
                     );
     }
   else
     {
      info.message = "No DCA positions found";
     }

   //Print("--- DCA Position Check ---");
   Print(info.message);

   return info;
  }

//+------------------------------------------------------------------+
//| Update hedge position stop loss to DCA target                     |
//+------------------------------------------------------------------+
bool UpdateHedgeStopLoss()
  {
   DCAPositionInfo dcaInfo = CheckDCAPositions();
   if(!dcaInfo.hasDCAPositions || dcaInfo.targetPrice <= 0)
     {
      //Print("No DCA positions or target price found to update hedge SL");
      return false;
     }

// Find hedge position
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) <= 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;

      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
        {
         string comment = PositionGetString(POSITION_COMMENT);
         if(StringFind(comment, "Hedge@") >= 0)
           {
            ulong ticket = PositionGetTicket(i);
            double currentSL = PositionGetDouble(POSITION_SL);

            // Only update if new SL is different
            if(MathAbs(currentSL - dcaInfo.targetPrice) > _Point)
              {
               //Print("Updating hedge position SL to DCA target price:");
               //Print("Ticket: ", ticket);
               //Print("Current SL: ", currentSL);
               //Print("New SL: ", dcaInfo.targetPrice);

               if(!ExtTrade.PositionModify(ticket, dcaInfo.targetPrice, 0))
                 {
                  //Print("Failed to update hedge SL: ", GetLastError());
                  return false;
                 }
               //Print("Successfully updated hedge SL to DCA target");
               return true;
              }
            else
              {
               //Print("Hedge SL already at DCA target price");
               return true;
              }
           }
        }
     }

   //Print("No hedge position found to update");
   return false;
  }

//+------------------------------------------------------------------+
//| Global variables for balance management                           |
//+------------------------------------------------------------------+
input double InInitialBalance = 2000.0;     // Initial trading balance
input double InProfitThreshold = 20000.0;    // Profit threshold to park money
input double InBalanceReserve = 4000.0;      // Amount to keep after parking

// Store parked balance - initialize in OnInit
double g_ParkedBalance = 0.0;
double g_LastParkingCheck = 0.0;  // Store last account balance when we parked money

//+------------------------------------------------------------------+
//| Get available balance for trading                                 |
//+------------------------------------------------------------------+
double GetAvailableBalance()
  {
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);

// Check if we need to park more money
   if(currentBalance > g_LastParkingCheck + InProfitThreshold + InBalanceReserve)
     {
      double profitToKeep = currentBalance - g_LastParkingCheck - InProfitThreshold;
      double newParking = currentBalance - profitToKeep;

      g_ParkedBalance = newParking;
      g_LastParkingCheck = currentBalance;

      Print("--- Balance Parking Update ---");
      Print("Current Balance: ", currentBalance);
      Print("Profit Threshold Reached");
      Print("New Parked Amount: ", g_ParkedBalance);
      Print("Available for Trading: ", profitToKeep);
     }

   double availableBalance = currentBalance - g_ParkedBalance;

   Print("--- Available Balance Check ---");
   Print("Total Account Balance: ", currentBalance);
   Print("Total Account Equity: ", currentEquity);
   Print("Parked Balance: ", g_ParkedBalance);
   Print("Available for Trading: ", availableBalance);
   Print("Last Parking Check At: ", g_LastParkingCheck);
   
   if (availableBalance < 0) return 0;
   return availableBalance;
  }

//+------------------------------------------------------------------+
//| Initialize balance management                                     |
//+------------------------------------------------------------------+
void InitializeBalanceManagement()
  {
// Reset parking values on start
   g_ParkedBalance = 0.0;
   g_LastParkingCheck = GetAvailableBalance();

   //Print("--- Balance Management Initialized ---");
   //Print("Initial Balance: ", InInitialBalance);
   //Print("Profit Threshold: ", InProfitThreshold);
   //Print("Balance Reserve: ", InBalanceReserve);
   //Print("Starting Account Balance: ", g_LastParkingCheck);
  }

//+------------------------------------------------------------------+
//| Get balance management status                                     |
//+------------------------------------------------------------------+
string GetBalanceStatus()
  {
   double currentBalance = GetAvailableBalance();
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);

   return StringFormat(
             "Balance Management Status:\n" +
             "Total Balance: %.2f\n" +
             "Total Equity: %.2f\n" +
             "Parked Balance: %.2f\n" +
             "Available Balance: %.2f\n" +
             "Last Parking Check: %.2f\n" +
             "Next Parking at: %.2f",
             currentBalance,
             currentEquity,
             g_ParkedBalance,
             currentBalance - g_ParkedBalance,
             g_LastParkingCheck,
             g_LastParkingCheck + InProfitThreshold
          );
  }
//+------------------------------------------------------------------+


//+------------------------------------------------------------------+
//| Close or partial close BUY positions based on profit/loss value  |
//+------------------------------------------------------------------+
void CloseLongsByProfitLoss(double targetValue)
{
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
        if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY) continue;

        double posProfit = PositionGetDouble(POSITION_PROFIT);
        double posVolume = PositionGetDouble(POSITION_VOLUME);

        // Check if profit/loss meets or exceeds the target
        if((targetValue >= 0 && posProfit >= targetValue) ||
           (targetValue < 0 && posProfit <= targetValue))
        {
            double closeVolume = posVolume;
            double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

            // If partial close is possible, close only the minimum lot
            if(posVolume > minLot)
            {
                closeVolume = minLot;
            }

            MqlTradeRequest request;
            MqlTradeResult result;
            ZeroMemory(request);
            ZeroMemory(result);

            request.action   = TRADE_ACTION_DEAL;
            request.symbol   = _Symbol;
            request.position = ticket;
            request.volume   = closeVolume;
            request.type     = ORDER_TYPE_SELL; // To close a BUY position
            request.price    = price;
            request.deviation= 10;
            request.magic    = MagicNumber;
            request.comment  = "Escape Close Losing trade@" + price;

            if(!OrderSend(request, result))
            {
                //Print("Failed to close position #", ticket, " Error: ", GetLastError());
            }
            else
            {
                //Print("Closed ", closeVolume, " lots of BUY position #", ticket, " at profit/loss: ", posProfit);
            }
        }
    }
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                       const MqlTradeRequest &request,
                       const MqlTradeResult &result)
{
    //Print("╔════════════════════════════════════════════╗");
    //Print("║ Trade Transaction Triggered                 ║");
    //Print("╚════════════════════════════════════════════╝");

    if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
    {
        ulong deal_ticket = trans.deal;
        if(HistoryDealSelect(deal_ticket))
        {
            // Get the original position details
            long position_ticket = HistoryDealGetInteger(deal_ticket, DEAL_POSITION_ID);
            
            // Get the original position's comment
            string originalComment = "";
            if(HistorySelectByPosition(position_ticket))
            {
                int dealsTotal = HistoryDealsTotal();
                for(int i = 0; i < dealsTotal; i++)
                {
                    ulong dealTicket = HistoryDealGetTicket(i);
                    if(HistoryDealGetInteger(dealTicket, DEAL_ENTRY) == DEAL_ENTRY_IN)
                    {
                        originalComment = HistoryDealGetString(dealTicket, DEAL_COMMENT);
                        break;
                    }
                }
            }

            //Print("Original Position Comment: ", originalComment);
            
            // Check if this was our hedge position
            if(StringFind(originalComment, "Hedge@") >= 0)
            {
                
                double deal_profit = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
                long deal_type = HistoryDealGetInteger(deal_ticket, DEAL_TYPE);
                long deal_reason = HistoryDealGetInteger(deal_ticket, DEAL_REASON);
                deal_profit = CalculatePositionProfit(position_ticket);
                //Print("Found Hedge Position:");
                //Print("  - Position ID: ", position_ticket);
                //Print("  - Deal Profit: ", deal_profit);
                //Print("  - Deal Type: ", deal_type);
                //Print("  - Close Reason: ", deal_reason);
                
                // Check if it was closed by TP
                if((true && deal_profit > 0 ) || (deal_type == DEAL_TYPE_BUY && deal_reason == DEAL_REASON_TP))
                {
                    total_deal_profit += deal_profit;
                    Print("╔════════════════════════════════════════════╗");
                    Print("║ HEDGE POSITION TP HIT - CLOSING LONGS      ║");
                    Print("╚════════════════════════════════════════════╝");
                    Print("Hedge Position #", position_ticket, " closed with profit: ",deal_profit, " total hedge profit: ", total_deal_profit );
                    
                    // Close long positions with the same profit amount
                    CloseHedgedLongs(deal_profit);
                    // Instead of close the hedged long, we will readjust the DCA TP
                    //AdjustLongPositionsTP(total_deal_profit);
                    //OpenReduceShortPosition(total_deal_profit * 0.8);
                    
                    //double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
                    //double equityChange = currentEquity - ReduceStartingBalance;
                    //double reductionAmount = deal_profit * 0.8;
                    //if(reductionAmount > 0)
                    //{
                    //  //Print("Closing partial longs for loss: ", reductionAmount, " (hedge profit: ", deal_profit, ", equity change: ", equityChange, ")");
                    //  CloseLongsForLoss(reductionAmount);
                    //}
                    //else
                    //{
                    //  //Print("No reduction needed, equity change exceeds hedge profit.");
                    //}
                }
                
                if (deal_reason == DEAL_REASON_SL) {
                    LastHedgePrice = 0;
                    
                }
                
            } else {
                //long deal_reason = HistoryDealGetInteger(deal_ticket, DEAL_REASON);
               // if (deal_reason == DEAL_REASON_SL) {
                   IsSellStopHedge = false;
                    
                //}

            
            }
            
        }
    }
}


//+------------------------------------------------------------------+
//| Close long positions based on hedge profit                        |
//+------------------------------------------------------------------+
void CloseHedgedLongs(double hedgeProfit)
{
    //Print("Attempting to close long positions to match hedge profit: ", hedgeProfit);
    
    // First, calculate total profit of all long positions
    double totalLongProfit = 0;
    int totalLongs = 0;
    
    // Array to store position tickets and their profits
    int maxPositions = 100;  // adjust as needed
    ulong tickets[];
    double profits[];
    double volumes[];
    ArrayResize(tickets, maxPositions);
    ArrayResize(profits, maxPositions);
    ArrayResize(volumes, maxPositions);
    
    // First pass: gather all long positions
    //Print("=== Scanning Long Positions ===");
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
       ulong ticket = PositionGetTicket(i);
       if(!PositionSelectByTicket(ticket)) continue;
       if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
       if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
       if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY) continue;
       
       // Get position details
       double posProfit = PositionGetDouble(POSITION_PROFIT);
       double posVolume = PositionGetDouble(POSITION_VOLUME);
       double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
       double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
       string posComment = PositionGetString(POSITION_COMMENT);
       
       //Print("Position #", ticket, ":");
       //Print("  Volume: ", posVolume);
       //Print("  Open Price: ", openPrice);
       //Print("  Current Price: ", currentPrice);
       //Print("  Profit: ", posProfit);
       //Print("  Comment: ", posComment);
       
       // Store position details
       tickets[totalLongs] = ticket;
       profits[totalLongs] = posProfit;
       volumes[totalLongs] = posVolume;
       totalLongProfit += posProfit;
       totalLongs++;
    }
   
    //Print("=== Summary ===");
    //Print("Total Long Positions Found: ", totalLongs);
    //Print("Total Long Profit: ", totalLongProfit);
    
    //Print("Found ", totalLongs, " long positions with total profit: ", totalLongProfit);
    
    // Sort positions by profit (bubble sort - simple but effective for small arrays)
    for(int i = 0; i < totalLongs - 1; i++)
    {
        for(int j = 0; j < totalLongs - i - 1; j++)
        {
            if(profits[j] > profits[j + 1])
            {
                // Swap all arrays
                double tempProfit = profits[j];
                profits[j] = profits[j + 1];
                profits[j + 1] = tempProfit;
                
                ulong tempTicket = tickets[j];
                tickets[j] = tickets[j + 1];
                tickets[j + 1] = tempTicket;
                
                double tempVolume = volumes[j];
                volumes[j] = volumes[j + 1];
                volumes[j + 1] = tempVolume;
            }
        }
    }
    
    // Close positions until we match or exceed the hedge profit
    double closedProfit = 0;
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    
    for(int i = 0; i < totalLongs; i++)
    {
        if (profits[i] > 0) continue;
        if(!PositionSelectByTicket(tickets[i])) continue;
        
        double posVolume = volumes[i];
        double closeVolume = posVolume;
        
        // Calculate remaining profit needed
        double remainingProfitNeeded = hedgeProfit - closedProfit;
        
        // If this position's profit is more than needed, calculate partial close volume
        if(MathAbs(profits[i]) > remainingProfitNeeded && posVolume > minLot)
        {
            closeVolume = (remainingProfitNeeded / profits[i]) * posVolume;
            // Round to minimum lot size
            closeVolume = MathFloor(closeVolume / minLot) * minLot;
            if(closeVolume < minLot) closeVolume = minLot;
            //Print("Calculated partial close volume: ", closeVolume, " from original volume: ", posVolume, " based on remaining profit needed: ", remainingProfitNeeded,  " and position profit: ", profits[i]);
        }
        
        bool success = false;
        //if(closeVolume == posVolume)
        if (MathAbs(profits[i]) < hedgeProfit)
        {
            // Full close
            success = ExtTrade.PositionClose(tickets[i], 
            "Hedge full#" + IntegerToString(tickets[i]));
            //Print("Attempting full close of position #", tickets[i]);
        }
        else
        {
            // Partial close
            success = ExtTrade.PositionClosePartial(tickets[i], closeVolume,"Hedge partial#" + IntegerToString(tickets[i]));
            //Print("Attempting partial close of position #", tickets[i], " volume: ", closeVolume);
        }
        
        if(!success)
        {
            //Print("Failed to close position #", tickets[i], " Error: ", GetLastError());
        }
        else
        {
            double closedAmount = profits[i] * (closeVolume / posVolume);
            closedProfit += closedAmount;
            //Print("Closed ", closeVolume, " lots of position #", tickets[i], " Profit: ", closedAmount,  " Cumulative closed profit: ", closedProfit);
                  
            if(MathAbs(closedProfit) >= hedgeProfit)
            {
                //Print("Reached target hedge profit. Stopping closure.");
                break;
            }
        }
    }
    
    //Print("=== Hedge Closure Summary ===");
    //Print("Hedge Profit Target: ", hedgeProfit);
    //Print("Total Profit Closed: ", closedProfit);
    //Print("Difference: ", hedgeProfit - closedProfit);
}

//+------------------------------------------------------------------+
//| Calculate total profit for a position                             |
//+------------------------------------------------------------------+
double CalculatePositionTotalProfit(ulong ticket)
{
    if(!PositionSelectByTicket(ticket)) return 0;
    
    double posVolume = PositionGetDouble(POSITION_VOLUME);
    double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
    double currentPrice = PositionGetDouble(POSITION_PRICE_CURRENT);
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    
    // Calculate profit based on price difference
    double priceDiff = currentPrice - openPrice;
    double profit = priceDiff * posVolume * tickValue / tickSize;
    
    return profit;
}

//+------------------------------------------------------------------+
//| Close long positions based on hedge profit                        |
//+------------------------------------------------------------------+
void old_v1_CloseHedgedLongs(double hedgeProfit)
{
    //Print("Attempting to close long positions to match hedge profit: ", hedgeProfit);
    
    // First, calculate total profit of all long positions
    double totalLongProfit = 0;
    int totalLongs = 0;
    
    // Array to store position tickets and their profits
    int maxPositions = 100;  // adjust as needed
    ulong tickets[];
    double profits[];
    ArrayResize(tickets, maxPositions);
    ArrayResize(profits, maxPositions);
    
    // First pass: gather all long positions
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
        if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY) continue;
        
        // Store position details
        tickets[totalLongs] = ticket;
        profits[totalLongs] = PositionGetDouble(POSITION_PROFIT);
        totalLongProfit += profits[totalLongs];
        totalLongs++;
    }
    
    //Print("Found ", totalLongs, " long positions with total profit: ", totalLongProfit);
    
    // Sort positions by profit (bubble sort - simple but effective for small arrays)
    for(int i = 0; i < totalLongs - 1; i++)
    {
        for(int j = 0; j < totalLongs - i - 1; j++)
        {
            if(profits[j] > profits[j + 1])
            {
                // Swap profits
                double tempProfit = profits[j];
                profits[j] = profits[j + 1];
                profits[j + 1] = tempProfit;
                
                // Swap tickets
                ulong tempTicket = tickets[j];
                tickets[j] = tickets[j + 1];
                tickets[j + 1] = tempTicket;
            }
        }
    }
    
    // Close positions until we match or exceed the hedge profit
    double closedProfit = 0;
    
    for(int i = 0; i < totalLongs; i++)
    {
        if(!PositionSelectByTicket(tickets[i])) continue;
        
        double posVolume = PositionGetDouble(POSITION_VOLUME);
        
        MqlTradeRequest request = {};
        MqlTradeResult result = {};
        
        request.action = TRADE_ACTION_DEAL;
        request.position = tickets[i];
        request.symbol = _Symbol;
        request.volume = posVolume;
        request.type = ORDER_TYPE_SELL;
        request.price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        request.deviation = 10;
        request.magic = MagicNumber;
        request.comment = "Closed to match hedge profit";
        // Add fill type settings
        //request.type_filling = ORDER_FILLING_FOK; // Fill or Kill
        // Use the symbol's supported fill type
        request.type_filling = ORDER_FILLING_BOC;// (ENUM_ORDER_TYPE_FILLING)SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
        if(!OrderSend(request, result))
        {
            //Print("Failed to close position #", tickets[i], " Error: ", GetLastError());
        }
        else
        {
            closedProfit += profits[i];
            //Print("Closed position #", tickets[i], " Profit: ", profits[i],  " Cumulative closed profit: ", closedProfit);
                  
            if(closedProfit >= hedgeProfit)
            {
                //Print("Reached target hedge profit. Stopping closure.");
                break;
            }
        }
    }
    
    //Print("=== Hedge Closure Summary ===");
    //Print("Hedge Profit Target: ", hedgeProfit);
    //Print("Total Profit Closed: ", closedProfit);
    //Print("Difference: ", hedgeProfit - closedProfit);
}

//+------------------------------------------------------------------+
//| Hourly //Print Function                                             |
//+------------------------------------------------------------------+
datetime lastPrintTime = 0;  // Global variable to track last //Print time

void Print(string message)
{
    return ;
    datetime currentTime = TimeCurrent();
    
    // Check if an hour has passed since last //Print
    if(currentTime - lastPrintTime >= PeriodSeconds(PERIOD_H1))
    {
        // Get current time components for the log
        MqlDateTime time;
        TimeToStruct(currentTime, time);
        
        // Create timestamp
        string timestamp = StringFormat("[%04d.%02d.%02d %02d:%02d]", 
            time.year, time.mon, time.day, time.hour, time.min);
            
        // //Print with timestamp
        //Print(timestamp, " HOURLY LOG: ", message);
        
        // Update last //Print time
        lastPrintTime = currentTime;
    }
}

//+------------------------------------------------------------------+
//| Overloaded H//Print for multiple values                             |
//+------------------------------------------------------------------+
void Print(string message, double value)
{
    Print(message + ": " + DoubleToString(value, 2));
}

void Print(string message, int value)
{
    Print(message + ": " + IntegerToString(value));
}

//+------------------------------------------------------------------+
//| H//Print for array of values                                        |
//+------------------------------------------------------------------+
void Print(string message, double& values[])
{
    string arrayStr = "";
    for(int i = 0; i < ArraySize(values); i++)
    {
        if(i > 0) arrayStr += ", ";
        arrayStr += DoubleToString(values[i], 2);
    }
    Print(message + ": [" + arrayStr + "]");
}

//+------------------------------------------------------------------+
//| Force //Print regardless of time (for critical messages)            |
//+------------------------------------------------------------------+
void HForcePrint(string message)
{
    datetime currentTime = TimeCurrent();
    MqlDateTime time;
    TimeToStruct(currentTime, time);
    
    string timestamp = StringFormat("[%04d.%02d.%02d %02d:%02d]", 
        time.year, time.mon, time.day, time.hour, time.min);
        
    //Print(timestamp, " FORCED HOURLY LOG: ", message);
    lastPrintTime = currentTime;
}

//+------------------------------------------------------------------+
//| Calculate position profit from entry and exit prices              |
//+------------------------------------------------------------------+
double CalculatePositionProfit(long position_ticket)
{
    double profit = 0.0;
    double entry_price = 0.0;
    double exit_price = 0.0;
    double position_volume = 0.0;
    long position_type = -1;
    
    //Print("=== Calculating Profit for Position #", position_ticket, " ===");
    
    if(HistorySelectByPosition(position_ticket))
    {
        int total_deals = HistoryDealsTotal();
        //Print("Total deals found: ", total_deals);
        
        // Find entry and exit deals
        for(int i = 0; i < total_deals; i++)
        {
            ulong deal_ticket = HistoryDealGetTicket(i);
            if(deal_ticket <= 0) continue;
            
            long deal_entry = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
            
            if(deal_entry == DEAL_ENTRY_IN) // Opening deal
            {
                entry_price = HistoryDealGetDouble(deal_ticket, DEAL_PRICE);
                position_volume = HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
                position_type = HistoryDealGetInteger(deal_ticket, DEAL_TYPE);
                
                //Print("Entry Deal Found:");
                //Print("  Price: ", entry_price);
                //Print("  Volume: ", position_volume);
                //Print("  Type: ", position_type == DEAL_TYPE_BUY ? "BUY" : "SELL");
            }
            else if(deal_entry == DEAL_ENTRY_OUT) // Closing deal
            {
                exit_price = HistoryDealGetDouble(deal_ticket, DEAL_PRICE);
                //Print("Exit Deal Found:");
                //Print("  Price: ", exit_price);
                if (position_type == ORDER_TYPE_SELL) {
                   LastShortPrice = exit_price;
                   ShortActivated = false;
                }
            }
        }
        
        // Calculate profit
        if(entry_price > 0 && exit_price > 0 && position_volume > 0)
        {
            double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
            double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
            double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
            
            //Print("Calculation Parameters:");
            //Print("  Point: ", point);
            //Print("  Tick Value: ", tick_value);
            //Print("  Tick Size: ", tick_size);
            
            if(position_type == DEAL_TYPE_BUY)
            {
                profit = (exit_price - entry_price) * position_volume * tick_value / tick_size;
            }
            else if(position_type == DEAL_TYPE_SELL)
            {
                profit = (entry_price - exit_price) * position_volume * tick_value / tick_size;
            }
            
            //Print("Profit Calculation:");
            //Print("  Price Difference: ", MathAbs(exit_price - entry_price));
            //Print("  Raw Profit: ", profit);
        }
    }
    
    return profit;
}

//+------------------------------------------------------------------+
//| Adjust long positions' TP based on hedge profit                   |
//+------------------------------------------------------------------+
void AdjustLongPositionsTP(double hedgeProfit)
{
    //Print("=== Adjusting Long Positions TP Based on Hedge Profit: ", hedgeProfit, " ===");
    
    // Calculate average position details
    double totalVolume = 0;
    double volumePrice = 0;
    double totalProfit = 0;
    int totalPositions = 0;
    
    // Arrays for position tracking
    ulong tickets[];
    double volumes[];
    double openPrices[];
    double currentTPs[];
    ArrayResize(tickets, 100);
    ArrayResize(volumes, 100);
    ArrayResize(openPrices, 100);
    ArrayResize(currentTPs, 100);
    
    // First pass: gather position details and calculate averages
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
        if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY) continue;
        
        double posVolume = PositionGetDouble(POSITION_VOLUME);
        double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        double currentTP = PositionGetDouble(POSITION_TP);
        double posProfit = PositionGetDouble(POSITION_PROFIT);
        
        tickets[totalPositions] = ticket;
        volumes[totalPositions] = posVolume;
        openPrices[totalPositions] = openPrice;
        currentTPs[totalPositions] = currentTP;
        
        totalVolume += posVolume;
        volumePrice += posVolume * openPrice;
        totalProfit += posProfit;
        totalPositions++;
        
        //Print("Position #", ticket, ":");
        //Print("  Volume: ", posVolume);
        //Print("  Open Price: ", openPrice);
        //Print("  Current TP: ", currentTP);
        //Print("  Current Profit: ", posProfit);
    }
    
    if(totalPositions == 0)
    {
        //Print("No long positions found to adjust");
        return;
    }
    
    double averagePrice = volumePrice / totalVolume;
    
    // Get current ATR for TP calculation
    double atr[];
    ArraySetAsSeries(atr, true);
    if(CopyBuffer(ExtATRHandle, 0, 0, 1, atr) != 1)
    {
        //Print("Failed to get ATR value");
        return;
    }
    
    //Print("=== Position Analysis ===");
    //Print("Total Positions: ", totalPositions);
    //Print("Average Entry Price: ", averagePrice);
    //Print("Total Volume: ", totalVolume);
    //Print("Current ATR: ", atr[0]);
    //Print("Total Current Profit: ", totalProfit);
    
    // Calculate new TP based on ATR and hedge profit
    double profitPerLot = hedgeProfit / totalVolume;
    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    double atrMultiplier = TakeProfitATRMultiplier; // Your ATR multiplier input parameter
    
    // New TP calculation considering hedge profit
    double baseTP = averagePrice + (atr[0] * atrMultiplier);
    double adjustedTP = baseTP - (hedgeProfit * 0.1 / (totalVolume * 100000)); // Adjust based on hedge profit
    
    //Print("=== TP Calculation ===");
    //Print("Base TP (Average + ATR): ", baseTP);
    //Print("Adjusted TP (considering hedge): ", adjustedTP);
    
    // Update all positions with new TP
    for(int i = 0; i < totalPositions; i++)
    {
        if(!PositionSelectByTicket(tickets[i])) continue;
        
        if(!ExtTrade.PositionModify(tickets[i], 0, adjustedTP))
        {
            //Print("Failed to modify position #", tickets[i], " Error: ", GetLastError());
        }
        else
        {
            //Print("Updated position #", tickets[i], " with new TP: ", adjustedTP);
        }
    }
    
    //Print("=== TP Adjustment Summary ===");
    //Print("Hedge Profit Considered: ", hedgeProfit);
    //Print("New TP Level: ", adjustedTP);
    //Print("Positions Updated: ", totalPositions);
}

//+------------------------------------------------------------------+
//| Close all existing hedge positions                                |
//+------------------------------------------------------------------+
void CloseAllHedgePositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(!PositionSelectByTicket(ticket)) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;
      
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL &&
         StringFind(PositionGetString(POSITION_COMMENT), "Hedge@") >= 0)
      {
         //Print("Closing existing hedge position #", ticket);
         if(!ExtTrade.PositionClose(ticket))
         {
            //Print("Error closing hedge position: ", GetLastError());
         }
      }
   }

   // Also delete any pending hedge orders
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong ticket = OrderGetTicket(i);
      if(!OrderSelect(ticket)) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
      if(OrderGetInteger(ORDER_MAGIC) != MagicNumber) continue;
      
      if(OrderGetInteger(ORDER_TYPE) == ORDER_TYPE_SELL_STOP &&
         StringFind(OrderGetString(ORDER_COMMENT), "Hedge@") >= 0)
      {
         //Print("Deleting existing hedge sell stop order #", ticket);
         if(!ExtTrade.OrderDelete(ticket))
         {
            //Print("Error deleting hedge order: ", GetLastError());
         }
      }
   }
}


void OpenReduceShortPosition(double profitToReduce)
{
    double avgLongPrice = CalculateAveragePrice();
    double totalLongVolume = GetTotalLongVolume();
    if(totalLongVolume <= 0 || avgLongPrice <= 0)
    {
        //Print("No long positions to reduce against.");
        return;
    }

    // Calculate the volume to reduce: profitToReduce / (avgLongPrice * tick value per lot / tick size)
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

    // Calculate how many "points" of price movement the profit represents
    double points = profitToReduce / (totalLongVolume * tickValue / tickSize);

    // Calculate the volume needed to offset this profit at the current price
    double reduceVolume = profitToReduce / (avgLongPrice * tickValue / tickSize);
    // Or, simply use a risk-based or fixed fraction of totalLongVolume if you prefer

    // Normalize volume
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    reduceVolume = MathMax(minLot, MathFloor(reduceVolume / lotStep) * lotStep);

    double price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double sl = 0; // You may want to set a stop loss
    double tp = 0; // You may want to set a take profit

    //Print("Opening Reduce Short: Volume=", reduceVolume, " at price=", price, " to offset profit=", profitToReduce);
    if(!ExtTrade.PositionOpen(_Symbol, ORDER_TYPE_SELL, reduceVolume, price, sl, tp, "Reduce@" + DoubleToString(price, Digits())))
    {
        //Print("Failed to open Reduce short position. Error: ", GetLastError());
    } else {
        IsReduceJourneyStarted = true;
        
    }
}

void CheckReduceSuccess()
{
    // Calculate total Reduce short volume and average price
    double totalReduceVolume = 0;
    double weightedReducePrice = 0;
    double totalLongVolume = 0;
    double weightedLongPrice = 0;

    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;

        double posVolume = PositionGetDouble(POSITION_VOLUME);
        double posPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        string comment = PositionGetString(POSITION_COMMENT);

        if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL && StringFind(comment, "Reduce@") >= 0)
        {
            totalReduceVolume += posVolume;
            weightedReducePrice += posPrice * posVolume;
        }
        if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
        {
            totalLongVolume += posVolume;
            weightedLongPrice += posPrice * posVolume;
        }
    }

    double avgReducePrice = (totalReduceVolume > 0) ? weightedReducePrice / totalReduceVolume : 0;
    double avgLongPrice = (totalLongVolume > 0) ? weightedLongPrice / totalLongVolume : 0;

    double reduceValue = avgReducePrice * totalReduceVolume;
    double longValue = avgLongPrice * totalLongVolume;

    //Print("Reduce Short Value: ", reduceValue, " | Long Value: ", longValue);

    double rescueTargetEquity = AccountInfoDouble(ACCOUNT_BALANCE); /* set this to your desired target, e.g. initial balance or a profit target */;
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY) ;
    if(reduceValue >= longValue && currentEquity >= rescueTargetEquity)
    {
       //Print("Rescue Succeed! Reduce shorts now match long exposure and equity target met.");
       //Print("Summary: Avg Reduce Price=", avgReducePrice, " Volume=", totalReduceVolume," | Avg Long Price=", avgLongPrice, " Volume=", totalLongVolume," \r\n| Equity: ", AccountInfoDouble(ACCOUNT_EQUITY), " Starting Balance ", ReduceStartingBalance);
   
       if (!PortfolioTrailingActive)
           StartPortfolioTrailing();
    }
    else
    {
       //Print("Rescue not yet complete. ReduceValue: ", reduceValue, " LongValue: ", longValue," Equity: ", AccountInfoDouble(ACCOUNT_EQUITY), " Target: ", rescueTargetEquity," \r\r Starting Balance ", ReduceStartingBalance);
             
                
       if (!PortfolioTrailingActive && ReduceStartingBalance >= rescueTargetEquity)
           StartPortfolioTrailing();
    }
    
    
}

void old_CheckReduceSuccess()
{
    // Calculate total Reduce short volume and average price
    double totalReduceVolume = 0;
    double weightedReducePrice = 0;
    double totalLongVolume = 0;
    double weightedLongPrice = 0;

    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(!PositionSelectByTicket(ticket)) continue;
        if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != MagicNumber) continue;

        double posVolume = PositionGetDouble(POSITION_VOLUME);
        double posPrice = PositionGetDouble(POSITION_PRICE_OPEN);
        string comment = PositionGetString(POSITION_COMMENT);

        if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL && StringFind(comment, "Reduce@") >= 0)
        {
            totalReduceVolume += posVolume;
            weightedReducePrice += posPrice * posVolume;
        }
        if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
        {
            totalLongVolume += posVolume;
            weightedLongPrice += posPrice * posVolume;
        }
    }

    double avgReducePrice = (totalReduceVolume > 0) ? weightedReducePrice / totalReduceVolume : 0;
    double avgLongPrice = (totalLongVolume > 0) ? weightedLongPrice / totalLongVolume : 0;

    double reduceValue = avgReducePrice * totalReduceVolume;
    double longValue = avgLongPrice * totalLongVolume;

    //Print("Reduce Short Value: ", reduceValue, " | Long Value: ", longValue);

    if(MathAbs(reduceValue - longValue) < 1e-2) // Tolerance for floating point
    {
        //Print("Rescue Succeed! Reduce shorts now match long exposure.");
        //Print("Summary: Avg Reduce Price=", avgReducePrice, " Volume=", totalReduceVolume, " | Avg Long Price=", avgLongPrice, " Volume=", totalLongVolume);
    }
}

void StartPortfolioTrailing()
{
    PortfolioTrailingActive = true;
    PortfolioTrailingPeak = GetPortfolioFloatingProfit();
    PortfolioTrailingStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    //Print("Portfolio trailing stop activated. Peak profit: ", PortfolioTrailingPeak);
}

double GetPortfolioFloatingProfit()
{
    double profit = 0.0;
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket) && PositionGetString(POSITION_SYMBOL) == _Symbol)
        {
            profit += PositionGetDouble(POSITION_PROFIT);
        }
    }
    return profit;
}

void CheckPortfolioTrailingStop()
{
    if(!PortfolioTrailingActive)
        return;

    double currentProfit = GetPortfolioFloatingProfit();
    double atr = GetATRValue();
    double trailingDistance = 2.0 * atr;
    
    //Print("Trailing Portfolio: trailing distance ", trailingDistance , " Current Profit: ", currentProfit, " Porfolio Peak: " , PortfolioTrailingPeak);
    
    if(currentProfit > PortfolioTrailingPeak)
    {
        PortfolioTrailingPeak = currentProfit;
        //Print("New portfolio profit peak: ", PortfolioTrailingPeak);
    }

    if(PortfolioTrailingPeak - currentProfit >= 8000)
    {
        //Print("╔════════════════════════════════════════════╗");
        //Print("║ Reduce rescue finally succeeded.               ║");
        //Print("╚════════════════════════════════════════════╝");
        //Print("Portfolio trailing stop triggered! Peak: ", PortfolioTrailingPeak, " Current: ", currentProfit, " Trailing: ", trailingDistance);
        CloseAllPositions();
        PortfolioTrailingActive = false;
        PortfolioTrailingPeak = 0;
        PortfolioTrailingStartEquity = 0;
        //Print("Reduce rescue finally succeeded. All positions closed.");
    }
}

void old_CheckPortfolioTrailingStop()
{
    if(!PortfolioTrailingActive)
        return;

    double currentProfit = GetPortfolioFloatingProfit();
    double atr = GetATRValue();
    double trailingDistance = 2.0 * atr;

    if(currentProfit > PortfolioTrailingPeak)
    {
        PortfolioTrailingPeak = currentProfit;
        //Print("New portfolio profit peak: ", PortfolioTrailingPeak);
    }

    if ((PortfolioTrailingPeak - currentProfit >= 0) || (PortfolioTrailingPeak > 0 && currentProfit <0 ))
    {
        //Print("╔════════════════════════════════════════════╗");
        //Print("║ Reduce rescue finally succeeded.               ║");
        //Print("╚════════════════════════════════════════════╝");
        //Print("Portfolio trailing stop triggered! Peak: ", PortfolioTrailingPeak, " Current: ", currentProfit, " Trailing: ", trailingDistance);
        CloseAllPositions();
        PortfolioTrailingActive = false;
        HedgeIsNeeded = false;
        //Print(" All positions closed.");
    }
}


void CloseAllPositions()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket) && PositionGetString(POSITION_SYMBOL) == _Symbol)
        {
            long type = PositionGetInteger(POSITION_TYPE);
            double volume = PositionGetDouble(POSITION_VOLUME);
            double price = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
            if(!ExtTrade.PositionClose(ticket))
            {
                //Print("Failed to close position: ", ticket, " Error: ", GetLastError());
            }
        }
    }
}

double GetATRValue()
{
    double atrValue[1];
    if(CopyBuffer(ExtATRHandle, 0, 0, 1, atrValue) != 1)
    {
        //Print("Failed to copy ATR buffer. Error: ", GetLastError());
        return 0.0; // Or some error value
    }
    return atrValue[0];
}


bool NoMoreLongPositions()
{
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket) && PositionGetString(POSITION_SYMBOL) == _Symbol)
        {
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                return false; // Found a long position
        }
    }
    return true; // No long positions found
}

void CloseLongsForLoss(double targetLoss)
{
    double remainingLoss = targetLoss;
    for(int i = PositionsTotal() - 1; i >= 0 && remainingLoss > 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket) && PositionGetString(POSITION_SYMBOL) == _Symbol)
        {
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
            {
                double posVolume = PositionGetDouble(POSITION_VOLUME);
                double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
                double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
                double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);

                // Calculate loss per lot for this position
                double lossPerLot = (openPrice - currentPrice) * contractSize;
                if(lossPerLot <= 0) continue; // Not a losing position

                // How much volume to close to realize remainingLoss?
                double volumeToClose = MathMin(posVolume, remainingLoss / lossPerLot);
                volumeToClose = NormalizeDouble(volumeToClose, 2); // 2 decimal places

                if(volumeToClose >= SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
                {
                    // Use ExtTrade to close the partial long position
                    if(!ExtTrade.PositionClosePartial(ticket, volumeToClose))
                    {
                        //Print("Failed to close partial long: ", GetLastError());
                    }
                    else
                    {
                        //Print("Closed ", volumeToClose, " lots of long position #", ticket, " for loss: ", volumeToClose * lossPerLot);
                        remainingLoss -= volumeToClose * lossPerLot;

                    }
                }
            }
        }
    }
}


//+------------------------------------------------------------------+
//| Draw an orange line from -20 bars to +20 bars                    |
//+------------------------------------------------------------------+
void DrawOrangeLine(string name, double price)
{
   // Delete any existing line with the same name
   ObjectDelete(0, name);
   
   // Get the current bar time
   datetime currentTime = iTime(_Symbol,PERIOD_H1, 0);
   
   // Calculate time for 20 bars back
   datetime startTime = iTime(_Symbol, PERIOD_H1, 20);
   
   // Calculate time for 20 bars forward (estimate based on bar interval)
   int barSeconds = PeriodSeconds(PERIOD_H1);
   datetime endTime = currentTime + (barSeconds * 20);
   
   // Create the line object
   ObjectCreate(0, name, OBJ_TREND, 0, startTime, price, endTime, price);
   
   // Set line properties
   ObjectSetInteger(0, name, OBJPROP_COLOR, clrOrange);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
   ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, false); // Don't extend to the right
   ObjectSetInteger(0, name, OBJPROP_BACK, false); // Draw on foreground
   
   // Refresh the chart
   ChartRedraw(1);
   
   //Print("Orange line drawn at price: ", price);
}