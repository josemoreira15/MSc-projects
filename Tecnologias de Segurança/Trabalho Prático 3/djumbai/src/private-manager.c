#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <pwd.h>

#include "../include/private-manager.h"



int add_private(const char* user1, const char* user2) {
    char command[256];
    char group[64];

    struct passwd *pwd1 = getpwnam(user1);
    struct passwd *pwd2 = getpwnam(user2);
    if (pwd1 == NULL || pwd2 == NULL) {
        printf("[djumbai-private-manager] both users must exist\n");
        return 1;
    }

    snprintf(group, sizeof(group), "%s-%s", user1, user2);
    snprintf(command, sizeof(command), "sudo groupadd %s", group);
    int call_result = system(command);

    if (call_result == -1) {
        printf("[djumbai-private-manager] error running the call\n");
        return 1;
    }

    char filename[128];
    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s.txt", group);
    FILE* file = fopen(filename, "w");
    fclose(file);

    snprintf(command, sizeof(command), "sudo chown :%s %s", group, filename);
    system(command);

    snprintf(command, sizeof(command), "sudo chmod 660 %s", filename);
    system(command);

    snprintf(command, sizeof(command), "sudo usermod -a -G %s %s", group, user1);
    system(command);

    snprintf(command, sizeof(command), "sudo usermod -a -G %s %s", group, user2);
    system(command);

    char message[128];
    snprintf(message, sizeof(message), "the private %s was created", group);
    new_log("djumbai-private-manager", message);

    return 0;
}


int del_private(const char* user1, const char* user2) {
    char group[64];
    char filename[128];

    snprintf(group, sizeof(group), "%s-%s", user1, user2);
    snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s.txt", group);

    if (access(filename, F_OK) == -1) {
        snprintf(group, sizeof(group), "%s-%s", user2, user1);
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/privates/%s.txt", group);
    }

    if (access(filename, F_OK) == -1) {
        printf("[djumbai-private-manager] the private does not exist\n");
        return 1;
    }

    char command[256];
    snprintf(command, sizeof(command), "sudo groupdel %s", group);
    int call_result = system(command);

    if (call_result == -1) {
        printf("[djumbai-private-manager] error running the call\n");
        return 1;
    }

    remove(filename);

    char message[128];
    snprintf(message, sizeof(message), "the private %s was deleted", group);
    new_log("djumbai-private-manager", message);

    return 0;
}


int main(int argc, char* argv[]) {
    int return_value = 0;

    if (geteuid() == 0 && system("sudo -n true") == 0) {
        if (argc == 4) {
            if (!strcmp(argv[1], "addprivate")) {
                return_value = add_private(argv[2], argv[3]);
            }

            else if (!strcmp(argv[1], "delprivate")) {
                return_value = del_private(argv[2], argv[3]);
            }

            else {
                printf("[djumbai-private-manager] invalid call\n");
                return_value = 1;
            }
        }

        else {
            printf("[djumbai-private-manager] invalid number of arguments\n");
            return_value = 1;
        }
    }

    else {
        printf("[djumbai-private-manager] can't execute without sudoer privileges\n");
        return_value = 1;
    }

    return return_value;
}