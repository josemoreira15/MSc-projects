#ifndef MAIL_CLIENT_H
#define MAIL_CLIENT_H

#include "message.h"
#include "controller.h"

int send_struct(int* arg, my_message m);
int request_email(int* arg, my_message m);

#endif