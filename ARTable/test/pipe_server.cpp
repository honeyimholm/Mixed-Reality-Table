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
  if (mkfifo("testfifo", 0666) < 0) {
    cout << "Error" << endl;
    return 1;
  }
  cout << "Connecting" << endl;
  if ((pipe = open("testfifo", O_WRONLY)) < 1) {
    cout << "Could not open pipe" << endl;
    return 1;
  }
  cout << "Connected" << endl;
  string test = "Test output";
  int len = test.size();
  if (write(pipe, "Test output", 12) < 0) {
    cout << "Could not write" << endl;
    return 1;
  }
  cout << "Sent message" << endl;
  close(pipe);
  return 0;
}
