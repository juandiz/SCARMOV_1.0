#include <WiFiNINA.h>
#include <WiFiUdp.h>

#include "frameManager.h"
#include "config_file.h"
#include "porting_mcu.h"
#include "Timer.h"
#include "display_if.h"

// WIFI variables
int status = WL_IDLE_STATUS;  // init status 
String ssid[WIFI_SSDI_NUMBER] = SECRET_SSID;    // your network SSID (name)
String pass[WIFI_SSDI_NUMBER] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;             // your network key Index number (needed only for WEP)

// Management variables
uint32_t connection_status_timer = 0; // connection check timer
bool alreadyConnected = false;
char packetBuffer[MAX_WIFIPACK_SIZE]; //buffer to hold incoming packet
WiFiUDP Udp; // udp connection

char ip_set[20];

void WIFI_printStatus() {
  // print the SSID of the network you're attached to:
  PRINT_LINE("----------------- CONNECTION INFO -------------------------");
  display_println(0,10,"Connected . . . ",1);
  PRINT("SSID: ");
  PRINT_LINE(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  String ip_str = String(ip[0])+"."+String(ip[1])+"."+String(ip[2])+"."+String(ip[3]);
  char ip_char_array[ip_str.length()+1];
 
  // copying the contents of the
  // string to char array
  strcpy(ip_set, ip_str.c_str());

  delay(3000);
  display_clear();
  PRINT("IP Address: ");
  display_println(0,0,"IP Address: ",1);
  display_println(0,10,ip_set,1);
  display_println(0,20,"Port : ",1);
  char port_str[10];
  sprintf(port_str,"%d",LOCAL_PORT);
  display_println(50,20,port_str,1);
  PRINT_LINE(ip_set);
  PRINT("PORT : ");
  PRINT_LINE(LOCAL_PORT);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  PRINT("signal strength (RSSI):");
  PRINT(rssi);
  PRINT_LINE(" dBm");
  PRINT_LINE("------------------------------------------------------------");
}

int get_ip_config(char* ip){
  strcpy(ip,ip_set);
  return LOCAL_PORT;
}

void WIFI_init(){
  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    PRINT_LINE("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();

  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    PRINT_LINE("Please upgrade the firmware");
  }

  // attempt to connect to Wifi network:
  int wifi_config_id = 0;
  while (true) {

    int ssid_n = ssid[wifi_config_id].length();
    int pass_n = pass[wifi_config_id].length();
 
    // declaring character array
    char ssid_char[ssid_n + 1];
    char pass_char[pass_n+1];
 
    // copying the contents of the
    // string to char array
    strcpy(ssid_char, ssid[wifi_config_id].c_str());
    strcpy(pass_char, pass[wifi_config_id].c_str());

    PRINT("Attempting to connect to SSID: ");
    PRINT_LINE(ssid_char);

    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid_char,pass_char);
    if(status == WL_CONNECTED)
      break;
    else{
      PRINT("Connection ERROR with SSID: ");
      PRINT_LINE(ssid_char);
      wifi_config_id++;
      delay(2000);
    }
  }

  WIFI_printStatus();
  PRINT_LINE("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  Udp.begin(LOCAL_PORT);
}

void WIFI_send(char* data,int len){
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write(data, len);
    Udp.endPacket();
}

int WIFI_read(){

  // if there's data available, read a packet

  int packetSize = Udp.parsePacket();
  if (packetSize) {
      // read the packet into packetBufffer
      int len = Udp.read(packetBuffer, MAX_WIFIPACK_SIZE);
      readNewStringInput((uint8_t*)packetBuffer,len);
      return 1;
  }
  return 0;

}

// Weak management of connection
void CONTROL_connectionCallback(){
  connection_status_timer   = setTimerLoad(DISCONECT_TOUT);
  if (!alreadyConnected) {
    //Limpia el buffer de entrada:
    PRINT_LINE("Se ha establecido conexion");
    alreadyConnected = true;
    Udp.flush();
  }
}

//////////////////////////////////////////////////////////////////////////////
// MAIN LOOP
char data_send[200];
int send_len = 0;

/// Call this function with the hiegthst priority
bool WIFI_loop() {
  WIFI_read();
  //   ////////////////// CONNECTION SEND AND RECEIVE
  if(alreadyConnected){
    send_len = SEND_getNewString(data_send); // check if there is new msg to send

    // data in buffer if available
    if (send_len > 0){
        PRINT_LINE("-------------------------- Send data --------------------------------------");
        PRINT_LINE(data_send);
        WIFI_send(data_send, send_len);
        memset(data_send,0,send_len*sizeof(char));
        PRINT_LINE(data_send);
        PRINT_LINE("-------------------------- Send data --------------------------------------");
    }

    // check client connection
    if (isTimerExpired(connection_status_timer)){
      alreadyConnected = false; // wait to receive connection cmd
      PRINT_LINE("--------------------------- Response Time Out. Client disconnected --------------------------------------");
    }
  }
  return alreadyConnected;
}