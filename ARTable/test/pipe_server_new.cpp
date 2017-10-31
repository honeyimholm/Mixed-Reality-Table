#include <iostream>
#include <fstream>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <vector>
#include <sstream>
#include <iterator>

using namespace std;

int main(void) {
/*
  if (mkfifo("testfifo", 0666) < 0) {
    cout << "Error" << endl;
    return 1;
  }
*/
  std::ofstream pipe ("testfifo");
  std::vector<int> test;
  int num = 0;
  for (int i = 0; i < 1000; i++) {
    test.push_back(num);
    num++;
  }
  std::ostringstream oss;
  if (!test.empty()) {
    std::copy(test.begin(), test.end()-1,
	      std::ostream_iterator<int>(oss, ","));
    oss << test.back();
  }
/*
  while (1) {
    pipe << num << endl;
  }
*/
  pipe << oss.str() << endl;
  pipe.close();
  return 0;
}
