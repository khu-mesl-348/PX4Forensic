/****************************************************************************
 *
 *   Copyright (c) 2012-2022 PX4 Development Team. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 * 3. Neither the name PX4 nor the names of its contributors may be
 *    used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
 * OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 ****************************************************************************/

 /**
 * @file integrity_tools
 * Minimal application example for PX4 autopilot
 *
 * @author Example User <mail@example.com>
 */

#include "integrity_tools.h"

#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "sha3.h"

#define XSTR(x) #x
#define STR(x) XSTR(x)

const char* ID = "sju0924";
const char* PW = "1234";
const char* key = "sju0924:1234";


// void HMACList_init(void){

// }
bool is_logged_in = false;

__EXPORT void HMACList_add(const char* filename, int filenameLen){


   hmac_list item = {"",""};

   if(filenameLen > 40){
      PX4_INFO("File name is too long to store\n");
      return;
   }

   ssize_t size;
   int fd = open(filename, O_RDONLY | O_BINARY);
   PX4_INFO("key: %s",key);

   size = lseek(fd, 0, SEEK_END);

   char* buf = malloc(sizeof(char)*(size + strlen(key)));
   lseek(fd, 0, SEEK_SET);
   if( (size = read(fd, (char *)buf, size))<0){
      PX4_INFO("unvalid file: %s ", filename);
      return;
   }

   strcpy(buf+size,key);

   //PX4_INFO("File size is %ld", size);
	int result = sha3_hash(item.filehash, (int)out_length, (uint8_t *) buf, (int)(size+strlen), hash_bit, 0);

   strncpy(item.filename, filename, filenameLen);
   PX4_INFO("hash of %s is %s, result is %d\n",item.filename,item.filehash,result);

   close(fd);

   char* keyfile = malloc(sizeof(char)*(filenameLen+2));

   strncpy(keyfile, filename, filenameLen);
   *(keyfile+filenameLen) = 'h';
   *(keyfile+filenameLen+1) = '\0';
   PX4_INFO("hash file stored at %s", keyfile);
   fd = open((const char *) keyfile, O_WRONLY | O_BINARY|O_CREAT,0600);
   if(write(fd, (void *)&item, sizeof(hmac_list))<0){
      PX4_INFO("write failed BY %d ", errno);
   };

   close(fd);

}

//buf: sizeof(struct HMAC_list)
void HMAC_get(const char* filename, int filenameLen, void *buf){
   hmac_list item;
   ssize_t size;

   //파일명 길이 검사
   if(filenameLen > 40){
      PX4_INFO("File name is too long to store");
      return;
   }

   //HMAC 파일 불러오기
   char* keyfile = malloc(sizeof(char)*(filenameLen+1));
   strncpy(keyfile, filename, filenameLen);
   strncpy(keyfile+filenameLen,"h",1);
   *(keyfile+filenameLen+1) = '\0';

   int fd = open((const char *) keyfile, O_RDONLY | O_BINARY);

   lseek(fd, 0, SEEK_SET);
   if( (size = read(fd, (char *)&item, sizeof(hmac_list)))<0){
      PX4_INFO("unvalid file: %s ", keyfile);
      return;
   }

   strncpy(buf, (char *)item.filehash, out_length);

   close(fd);
}

int HMAC_file(const char* filename, int filenameLen, void *hmac_buf){
   if(filenameLen > 40){
      PX4_INFO("File name is too long to store");
      return -1;
   }

   //파일 및 키 불러오기
   int fd = open(filename, O_RDONLY | O_BINARY);
   PX4_INFO("key: %s",key);

   //파일 크기 구하기
   ssize_t size;
   size = lseek(fd, 0, SEEK_END);

   //파일 열기
   char *buf = malloc(sizeof(char)*(size + strlen(key)));
   lseek(fd, 0, SEEK_SET);
   if( (size = read(fd, buf, size))<0){
      PX4_INFO("unvalid file: %s ", filename);
      return -1;
   }

   //파일이름+키 함치기
   strcpy(buf+size,key);

   //PX4_INFO("File size is %ld", size);
	int result = sha3_hash(hmac_buf, (int)out_length, (uint8_t *) buf, (int)(size+strlen), hash_bit, 0);

   close(fd);
   return result;

}
__EXPORT bool HMAC_verify(const char* filename, int filenameLen){

   // 파일 해시화
   char hmac_file[out_length] , hmac[out_length];
   HMAC_file(filename, filenameLen, hmac_file);
   HMAC_get(filename, filenameLen, hmac);

   if(!strncmp(hmac, hmac_file, out_length)){
      PX4_INFO("verification success\n");
      return 1;
   }
   else {
      PX4_INFO("verification failed\n");
      return 0;
   }


}

__EXPORT bool user_verify(const char* _id, const char* _pw){
   if(!strcmp(_id, ID) && !strcmp(_pw, PW)){
      PX4_INFO("login success, %s", _id);
      is_logged_in = true;
      return 1;
   }
   else{
      PX4_INFO("login failed, %s", _id);
      is_logged_in = false;
      return 0;
   }
}
int integrity_tools_main(int argc, char *argv[])
{
   if (argc < 2) {
		PX4_INFO("Hello Sky!");
	}
   else if(!strcmp(argv[1], "login")){
      if(is_logged_in) printf("true\n");
      else printf("false\n");
   }
	else if (argc == 3 && !strcmp(argv[1], "hmac")) {
      //HMACList_init()
      HMACList_add(argv[2],strlen(argv[2]) );
   }
   else if(argc == 3 && !strcmp(argv[1], "verify")){
      HMAC_verify(argv[2], strlen(argv[2]));
   }

   return OK;
}
