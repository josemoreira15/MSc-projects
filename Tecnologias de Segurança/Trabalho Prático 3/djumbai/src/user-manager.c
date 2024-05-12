#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <pwd.h>

#include "../include/user-manager.h"



int manage_user(const char* call, const char* username) {
    if (!strcmp(call, "adduser") || !strcmp(call, "deluser")) {
        char command[256];
        snprintf(command, sizeof(command), "sudo %s %s", call, username);

        int call_result = system(command);
        if (call_result == -1) {
            printf("[djumbai-user-manager] error running the call\n");
            return 1;
        }

        char message[128];
        if (!strcmp(call, "adduser")) {
            snprintf(message, sizeof(message), "the user %s was created", username);
        }

        else {
            snprintf(command, sizeof(command), "sudo rm -rf /home/%s", username);
            int call_result = system(command);
            if (call_result == -1) {
                printf("[djumbai-user-manager] error running the call\n");
                return 1;
            }
                
            snprintf(message, sizeof(message), "the user %s was deleted", username);
        }
            
        new_log("djumbai-group-manager", message);
    }
        
    else {
        printf("[djumbai-user-manager] invalid call\n");
        return 1;
    }

    return 0;
}


int main(int argc, char* argv[]) {
    int return_value = 0;

    if (geteuid() == 0 && system("sudo -n true") == 0) {
        if (argc == 3) {
            return_value = manage_user(argv[1], argv[2]);
        }

        else {
            printf("[djumbai-user-manager] invalid number of arguments\n");
            return_value = 1;
        }
    }
    
    else {
        printf("[djumbai-user-manager] can't execute without sudoer privileges\n");
        return_value = 1;
    }

    return return_value;
}