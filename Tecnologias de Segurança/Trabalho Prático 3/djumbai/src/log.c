#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include "../include/log.h"



void new_log(const char* service, const char* log) {
    if (geteuid() == 0 && system("sudo -n true") == 0) {
        FILE *file = fopen("/var/log/djumbai.log", "a");

        time_t current_time;
        struct tm* time_info;
        char time_string[80];
        time(&current_time);
        time_info = localtime(&current_time);
        strftime(time_string, sizeof(time_string), "%Y-%m-%d %H:%M:%S", time_info);

        fprintf(file, "[%s] (%s) %s\n", service, time_string, log);
        fclose(file);
    }
}