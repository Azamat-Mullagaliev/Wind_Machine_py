#include <Servo.h>

Servo deploy;
Servo pitch;
Servo engine1;
Servo engine2;

void engineStart()
{
   engine1.attach(6);
   engine2.attach(7);
   engine1.writeMicroseconds(2300);
   engine2.writeMicroseconds(2300);  
   delay(2000);
   engine1.writeMicroseconds(800);
   engine2.writeMicroseconds(800);  
   delay(8000); //6000 если нет деплоя рамки
}

void shutDown()
{
  engine1.detach();
  engine2.detach();
  delay(1000);
  pitch.write(145);
  delay(500);
  deployServoWrite(30);
  delay(1500);
  pitch.detach();
  exit(0);
}

void deployServoWrite(int val)
{
    deploy.attach(4);
    deploy.write(val);
    delay(1300);
    deploy.detach();
}

void setup()
{
  deployServoWrite(169);
  
  pitch.attach(3);
  pitch.write(145);
  
  engineStart();

  pitch.write(40);
  
  
  Serial.begin(115200);
}

void loop()
{
  if (Serial.available()>1){
    char key = Serial.read();
    int val = Serial.parseInt();
    switch (key){
      case 'p': pitch.write(val);
        break;
      case 'd': deploy.write(val);
        break;
      case 'e': 
        if (val==1){
          engineStart();
        }
        else {
          engine1.writeMicroseconds(val); 
          engine2.writeMicroseconds(val);
          }
        break;
      case 'c': if(val==0)shutDown();
        break;
    }
  }
  
}
