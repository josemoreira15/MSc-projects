#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <pwd.h>

#include "../include/group-manager.h"



int manage_group(const char* call, const char* groupname) {
    char command[256];

    if (!strcmp(call, "groupadd")) {
        snprintf(command, sizeof(command), "sudo groupadd %s", groupname);
        int call_result = system(command);

        if (call_result == -1) {
            printf("[djumbai-group-manager] error running the call\n");
            return 1;
        }

        char filename[128];
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/groups/%s.txt", groupname);
        FILE* file = fopen(filename, "w");
        fclose(file);

        snprintf(command, sizeof(command), "sudo chown :%s %s", groupname, filename);
        system(command);

        snprintf(command, sizeof(command), "sudo chmod 660 %s", filename);
        system(command);


        char message[128];
        snprintf(message, sizeof(message), "the group %s was created", groupname);
        new_log("djumbai-group-manager", message);
    }

    else if (!strcmp(call, "groupdel")) {
        snprintf(command, sizeof(command), "sudo groupdel %s", groupname);
        int call_result = system(command);

        if (call_result == -1) {
            printf("[djumbai-group-manager] error running the call\n");
            return 1;
        }

        char filename[128];
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/groups/%s.txt", groupname);
        remove(filename);

        char message[128];
        snprintf(message, sizeof(message), "the group %s was deleted", groupname);
        new_log("djumbai-group-manager", message);
    }

    else {
        printf("[djumbai-group-manager] invalid call\n");
        return 1;
    }

    return 0;
}


int manage_user_group(const char* call, const char* username, const char* groupname) {
    char command[100];
    
    if (!strcmp(call, "addusergroup")) {
        snprintf(command, sizeof(command), "sudo usermod -a -G %s %s", groupname, username);
        int call_result = system(command);

        if (!strcmp(groupname, "djumbai") && call_result != -1) {
            char filename[128];
            snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/users/%s.txt", username);
            FILE* file = fopen(filename, "w");
            fclose(file);
            chmod(filename, S_IRUSR | S_IWUSR);
            chown(filename, getpwnam(username)->pw_uid, -1);

            snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/server/%s.txt", username);
            file = fopen(filename, "w");
            fclose(file);
            chmod(filename, S_IRUSR | S_IWUSR);
            chown(filename, getpwnam("djumbai-server")->pw_uid, -1);
        }

        char message[128];
        snprintf(message, sizeof(message), "the user %s was added to the group %s", username, groupname);
        new_log("djumbai-group-manager", message);
    } 
    
    else if (!strcmp(call, "delusergroup")) {
        snprintf(command, sizeof(command), "sudo deluser %s %s", username, groupname);
        int call_result = system(command);

        if (!strcmp(groupname, "djumbai") && call_result != -1) {
            char filename[128];
            snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/users/%s.txt", username);
            remove(filename);

            snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/server/%s.txt", username);
            remove(filename);
        }

        char message[128];
        snprintf(message, sizeof(message), "the user %s was removed from the group %s", username, groupname);
        new_log("djumbai-group-manager", message);
    } 
    
    else {
        printf("[djumbai-group-manager] invalid call\n");
        return 1;
    }

    return 0;
}


int main(int argc, char* argv[]) {
    int return_value = 0;

    if (geteuid() == 0 && system("sudo -n true") == 0) {
        if (argc == 3) {
            return_value = manage_group(argv[1], argv[2]);
            
        }

        else if (argc == 4) {
            return_value = manage_user_group(argv[1], argv[2], argv[3]);
        }

        else {
            printf("[djumbai-group-manager] invalid number of arguments\n");
            return_value = 1;
        }
    }

    else {
        printf("[djumbai-group-manager] can't execute without sudoer privileges\n");
        return_value = 1;
    }

    return return_value;
}