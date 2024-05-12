#ifndef GROUPS_H
#define GROUPS_H

#include "../include/log.h"

int manage_group(const char* call, const char* groupname);
int manage_user_group(const char* call, const char* username, const char* groupname);

#endif