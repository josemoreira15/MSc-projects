#ifndef MESSAGE_H
#define MESSAGE_H

#define PORT 8080
#define BUFFER_SIZE 1024
#define USERLEN 32

typedef struct message {
    char user[USERLEN];
    char buff[BUFFER_SIZE]; 
    char target[USERLEN];
    int message_type;
    int sockid;
} my_message;

#endif