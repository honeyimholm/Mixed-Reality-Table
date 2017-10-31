#include <iostream>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

using namespace std;

int main(void) {
  int number, pipe;
  cout << "Connecting" << endl;
  if ((pipe = open("testfifo", O_RDONLY)) == -1) {
    cout << "Could not open pipe" << endl;
    return 1;
  }
  cout << "Connected" << endl;
  string test;
  char buf[12];
  int len = 12;
  if (read(pipe, buf, len) < 0) {
    cout << "Could not read" << endl;
    return 1;
  }
  cout << "Successfully read:" << endl;
  cout << buf << endl;
  close(pipe);
  return 0;
}
