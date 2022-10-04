#include <msp430.h>
#include <stdio.h>
#include <stdbool.h>
volatile unsigned int ADC_Result;

void initClocks(){
    // Set XT1CLK as ACLK source
    CSCTL4 |= SELA__XT1CLK;
    // Use external clock in low-frequency mode
    CSCTL6 |= XT1BYPASS_1 | XTS_0;
}


void GPIO(){
    P2DIR &=~BIT3; // &=~0x08
    P4DIR &=~BIT1;
    //  P2REN=0x08;
    P2REN |=0x08; // OR |= BIT3
    P4REN |=BIT1;
    //  P2OUT=0x08;
    P2OUT |=0x08; // OR |= BIT3
    P4OUT |=BIT1;
}

bool buttonPressedFire1() {
    if((P4IN & BIT1)==0x00) {
        __delay_cycles(10000); //used for de-bouncing

        if((P4IN & BIT1)==0x00) {
            return true;
        }
    }

    return false;
}

bool buttonPressedFire2() {
    if((P2IN & BIT3)==0x00) {
        __delay_cycles(10000); //used for de-bouncing

        if((P2IN & BIT3)==0x00) {
            return true;
        }
    }

    return false;
}

void initADC(){
    ADCCTL0 |=ADCSHT_1 | ADCON;
    ADCCTL1 |= ADCSHP | ADCSSEL_3;
    ADCCTL2 &=~ADCRES;
    ADCCTL2 |=ADCRES_0;
    ADCMCTL0 |=ADCINCH_9 | ADCSREF_0;
}


void initUart1(){
    // Configure UART pins
    P4SEL0 |= BIT3 | BIT2;                    // set 2-UART pin as second function
    //P4SEL0 &= ~(BIT3 | BIT2);

    // Configure UART
    UCA1CTLW0 = UCSWRST;                     // Hold UART in reset state

    UCA1CTLW0 |= UCSSEL__ACLK;               // CLK = ACLK
    // Baud Rate calculation
    // 32768/(9600) = 3.4133
    // Fractional portion = 0.4133
    // User's Guide Table 17-4: 0x92
    UCA1BR0 = 3;                             // 32768/9600
    UCA1BR1 = 0;
    UCA1MCTLW |= 0x9200;    //0x9200 is UCBRSx = 0x92

    UCA1CTLW0 &= ~UCSWRST;                    // Release reset state for operation
    UCA1IE |= UCRXIE;                         // Enable USCI_A0 RX interrupt
}

int main(void)
{

  WDTCTL = WDTPW | WDTHOLD;                // Stop watchdog timer
  PM5CTL0 &= ~LOCKLPM5;
  P1SEL0 |=BIT1;
  P2SEL1 |=BIT1;
  initADC();
  GPIO();
  initClocks();
  initUart1();

  __enable_interrupt();

  while(1){
      adc_read();
      Buff_Write(ADC_Result);
      if(buttonPressedFire2()||buttonPressedFire1()){
          Buff_Write(255);
      }
      __delay_cycles(10000);
  }
}

void adc_read(){
     ADCCTL0 |=ADCENC | ADCSC;

         while(ADCCTL1 & ADCBUSY) {
             ADC_Result=ADCMEM0-1;
         }
}

void Buff_Write(int val){
    while(!(UCA1IFG & UCTXIFG));
    UCA1TXBUF=val;
}

#pragma vector=USCI_A1_VECTOR
__interrupt void USCI_A1_ISR(void)
{
  UCA1TXBUF = UCA1RXBUF;
  __no_operation();

  // Clear flag
  UCA1IFG = 0;
}
