#include <Servo.h>

#define  baudrate 9600  // com port speed. Must match your setting
#define distancex 1  // x servo rotation steps
#define distancey 1  // y servo rotation steps

int val = 0;
int posx = 0;
int posy=0;

 
Servo pin2;
Servo pin3;
Servo pin4;
Servo pin5;
Servo pin6;
Servo pin7;
 
void setup() {
  Serial.begin(baudrate);        // connect to the serial port
  Serial.setTimeout(20);
  Serial.println("Starting Cam-servo Face tracker");
 
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);      
  
  pin2.attach(2);
  pin3.attach(3);
  pin4.attach(4);
  pin5.attach(5);
  pin6.attach(6);
  pin7.attach(7);
  
  // center servos
  pin2.write(175);   //axis
  pin3.write(90);
  pin4.write(90);
  pin5.write(100);   //base
  pin6.write(90);
  pin7.write(20);     //down01
  
  delay(200);
}
 
 
void loop () {

  while (Serial.available() <= 0); // wait for incoming serial data

  if(Serial.available() >= 1){

    val = 11;
    
    val = Serial.parseInt();

    posx = pin5.read();
    posy = pin7.read();
    
    if(val == 11){

      posx = posx -= distancex;
      posy = posy += distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);
        pin7.write(posy);
       
       }       
    }
    else if(val == 12){
      posx = posx -= distancex;
      posy = posy -= distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);
        pin7.write(posy);
       
       }      
    }
    else if(val == 21){
      posx = posx += distancex;
      posy = posy += distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);
        pin7.write(posy);
       
       }      
    }
    else if(val == 22){
      posx = posx += distancex;
      posy = posy -= distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);
        pin7.write(posy);
       
       }      
    }
     else if(val == 10){
      posx = posx -= distancex;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);

       
       }      
    }
     else if(val == 20){
      posx = posx += distancex;

          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        
        pin5.write(posx);

       
       }      
    }
     else if(val == 01){

      posy = posy += distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        

        pin7.write(posy);
       
       }      
    }
      else if(val == 02){

      posy = posy -= distancey;
          
      if(posx > 5 && posx < 175 && posy > 5 && posy < 175){
        

        pin7.write(posy);
       
       }      
    }
  }
}
