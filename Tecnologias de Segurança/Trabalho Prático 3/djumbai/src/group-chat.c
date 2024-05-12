#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <grp.h>
#include <pwd.h>

#include "../include/group-chat.h"



int group_send(const char* group) {
    int is_member = is_member_of(group);
    if (is_member && strcmp(group, "djumbai")) {
        char filename[128];
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/groups/%s.txt", group);
        FILE* group_file = fopen(filename, "a");

        char buffer[513];
        printf("[djumbai-group-chat] type your message: ");
        fgets(buffer, sizeof(buffer), stdin);

        char* username = getenv("LOGNAME");

        fprintf(group_file, "[%s] ", username);
        fprintf(group_file, "%s", buffer);
        fclose(group_file);

        return 0;
    }

    else {
        printf("[djumbai-group-chat] can't send a message to the group %s\n", group);
        return 1;
    }
}


int group_read(const char* group) {
    int is_member = is_member_of(group);
    if (is_member && strcmp(group, "djumbai")) {
        char filename[128];
        snprintf(filename, sizeof(filename), "/usr/local/djumbai-memory/groups/%s.txt", group);
        FILE* group_file = fopen(filename, "r");

        char buffer[1024];
        while (fgets(buffer, 1024, group_file) != NULL) {
            printf("%s", buffer);
        }

        fclose(group_file);

        return 0;
    }

    else {
        printf("[djumbai-group-chat] can't read messages from the group %s\n", group);
        return 1;
    }
}


int main(int argc, char* argv[]) {
    int return_value = 0;
    if (is_member_of("djumbai")) {
        if (argc == 3) {
            if (!strcmp(argv[1], "sendgroup")) {
                return_value = group_send(argv[2]);
            }

            else if (!strcmp(argv[1], "readgroup")) {
                return_value = group_read(argv[2]);
            }

            else {
                printf("[djumbai-group-chat] invalid call\n");
                return_value = 1;
            }
        }

        else {
            printf("[djumbai-group-chat] invalid number of arguments\n");
            return_value = 1;
        }
    }

    else {
        printf("[djumbai-group-chat] can't execute without djumbaier privileges\n");
        return_value = 1;
    }

    return return_value;
}