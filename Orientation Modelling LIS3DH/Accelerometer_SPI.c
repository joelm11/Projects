#include <stdio.h>
#include <msp430.h> 
#include <stdint.h>

uint8_t outxyz[] = {0,0,0,0,0,0};
//char outxyz[] = {'a','b','c','d','e','f'};
void configurePins(){
    printf("Hit configure\n");
    WDTCTL = WDTPW | WDTHOLD;       // stop watchdog timer
    //cs pin setup
    P2DIR |= BIT3;
    P2OUT |= BIT3;
    //selecting function mode for SPI pins (USCB0)
    P3SEL |= BIT0 + BIT1 + BIT2;
    //configuring SPI
    UCB0CTL1 |= UCSSEL_2;   //selects main clock (SMCLK) MHz 25MHz//or is it 1 MHz
    UCB0BR1 = 0x01; //Figure out how to get the desired clock speed
    UCB0CTL0 |= UCCKPL + UCMSB + UCSYNC + UCMST;    //configuring SPI registers
    UCB0CTL1 &= ~UCSWRST;   // reset SPI module
    //configuring interrupts
    UCB0IE |= UCTXIE + UCRXIE;
    UCB0IFG &= ~UCTXIFG;
    UCB0IFG &= ~UCRXIFG;
    //configuring UART
    UCA1CTLW0 |= UCSWRST;
    UCA1CTL1 |= UCSSEL__SMCLK;
    UCA1BR0 = 17; // Want 115200 baud //baud currently 57600
    UCA1MCTL |= UCBRS_3; //57600 baud
    //UCA1BR0 = 8;
    //UCA1MCTL |= UCBRS_6;//From datasheet for 115200 baud
    P4SEL |= BIT4;
    UCA1CTLW0 &= ~UCSWRST;
    UCA1IE |= UCTXIE;
}

uint8_t spiTransfer(uint8_t writeData)
{
    UCB0TXBUF = writeData;
    while(!(UCB0IFG & UCRXIFG)); // wait for RX buffer ready
    return UCB0RXBUF;
}

void setWriteMode(uint8_t addr)
{
    P2OUT &= ~BIT3;
    spiTransfer(addr | 0x00);
}

void setReadMode(uint8_t addr)
{
    P2OUT &= ~BIT3;
    spiTransfer(addr | 0x80);
}

void writeByte(uint8_t data)
{
    spiTransfer(data);
    P2OUT |= BIT3;
}

uint8_t readByte()
{
    uint8_t temp = spiTransfer(0xAA);
    P2OUT |= BIT3;
    return temp;
}

void confirmConnection(uint8_t address){
    setReadMode(address);
    int temp = readByte();
    if(temp == 51)
        printf("Connection success\n");
    else
        printf("Connection failed\n");
}

void send_to_terminal(uint8_t datalow, uint8_t datahigh){
    while(!(UCA1IFG & UCTXIFG));
         UCA1TXBUF = datahigh;
         __delay_cycles(100);
         printf("low: %d, high: %d\n",datalow,datahigh);
}

void xyz_to_terminal(){
    while(!(UCA1IFG & UCTXIFG));
    UCA1TXBUF = 0x40;
    int n;
    for(n = 0; n < 6; n++){
        while(!(UCA1IFG & UCTXIFG));
        UCA1TXBUF = outxyz[n];
        __delay_cycles(1000);
    }

}
void readAccZ(){
    setReadMode(0b00101100);
    uint8_t zLow = readByte();
    setReadMode(0b00101101);
    uint8_t zHigh = readByte();
    int16_t zData = 0;
    zData |= zLow;
    zData |= zHigh << 8;
    outxyz[0] = zLow;
    outxyz[1] = zHigh;
}

void readAccX(){
    setReadMode(0b00101000);
    uint8_t xLow = readByte();
    setReadMode(0b00101001);
    uint8_t xHigh = readByte();
    int16_t xData = 0;
    xData |= xLow;
    xData |= xHigh << 8;
    outxyz[4] = xLow;
    outxyz[5] = xHigh;
}

void readAccY(){
    setReadMode(0b00101010);
    uint8_t yLow = readByte();
    setReadMode(0b00101011);
    uint8_t yHigh = readByte();
    int16_t yData = 0;
    yData |= yLow;
    yData |= yHigh << 8;
    outxyz[2] = yLow;
    outxyz[3] = yHigh;
}

void testx(){
    setReadMode(0b00101000);
    int temp = readByte();
    setReadMode(0b00101000);
    int temp2 = readByte();
    printf("xLow: %d xHigh: %d\n",temp, temp2);

}

void readRegister(uint8_t address){
    setReadMode(address);
    int temp = readByte();
    printf("Register value: %d\n",temp);
}

int main(void)
{
    configurePins();
    UCB0IFG &= ~UCTXIFG;
    UCB0IFG &= ~UCRXIFG;
    confirmConnection(0b00001111);
    setWriteMode(0x20);
    writeByte(0b10011111);
    readRegister(0x20);

while(1){
            setReadMode(0x27);
            int temp = readByte();
            if(temp & 0b00001000){
                if(temp & 0b10000000){
                    readAccX();
                    readAccY();
                    readAccZ();
                    xyz_to_terminal();
                }
            }
    }
    return 0;
}


