#ifndef MAIL_SERVER_H
#define MAIL_SERVER_H

#include "message.h"
#include "controller.h"

int send_email(my_message message, void* arg, pthread_mutex_t mutex1);
int request_email(my_message message, void* arg, pthread_mutex_t mutex1);
void* handle_client(void* arg);

#endif