#include <iostream>
#include <fstream>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

using namespace std;

int main(void) {
  std::ifstream pipe ("testfifo");
  std::string line;
  while (1) {
    pipe >> line;
    if (pipe.eof()) {
      sleep(1);
      pipe.clear();
    } else {
      cout << line << endl;
    }
  }
  pipe.close();
  return 0;
}
