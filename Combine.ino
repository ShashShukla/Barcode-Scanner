 //Coil A
const int motorPin1  = 8;  // Pin 14 of L293
const int motorPin2  = 9;  // Pin 10 of L293
//Coil B
const int motorPin3  = 10; // Pin  7 of L293
const int motorPin4  = 11; // Pin  2 of L293
float i = 0;
bool x=0,y=0;

void setup(){
  pinMode(A0,INPUT);
  pinMode(2, INPUT_PULLUP);
  //attachInterrupt(digitalPinToInterrupt(2), ISR_EDL, FALLING);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
  Serial.begin(9600);
  x = digitalRead(2);
}

void scan(){
  for(i=0.0;i<=410;i+=0.05){
    analogWrite(motorPin1, max(0,255*sin(i)));
    analogWrite(motorPin2, max(0,-255*sin(i)));
    analogWrite(motorPin3, max(0,255*cos(i)));
    analogWrite(motorPin4, max(0,-255*cos(i)));
    if(((int)(20*i))%10 == 0)
      Serial.println(analogRead(A0));
  }
  for(;i>0;i-=0.05){
    analogWrite(motorPin1, max(0,255*sin(i)));
    analogWrite(motorPin2, max(0,-255*sin(i)));
    analogWrite(motorPin3, max(0,255*cos(i)));
    analogWrite(motorPin4, max(0,-255*cos(i)));
    if(((int)(20*i))%10 == 0)
      Serial.println(analogRead(A0));
  }
  analogWrite(motorPin1,0);
  analogWrite(motorPin2,0);
  analogWrite(motorPin3,0);
  analogWrite(motorPin4,0);
}

void loop(){
  y = digitalRead(2);
  if(x==1 && y==0)
    scan();
  x = y;
  delay(10);
}
