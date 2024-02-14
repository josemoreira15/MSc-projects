CC = gcc
SRC = src/
CFLAGS = -g -fno-omit-frame-pointer -pg -O3 -march=native -mavx -ftree-vectorize -msse4

.DEFAULT_GOAL = MD.exe

MD.exe: $(SRC)/MD.cpp
	$(CC) $(CFLAGS) $(SRC)MD.cpp -lm -o MD.exe

clean:
	rm ./MD.exe cp_output.txt cp_traj.xyz cp_average.txt

run:
	srun --partition=cpar perf stat -e instructions,cycles ./MD.exe < inputdata.txt

assembly:
	$(CC) $(CFLAGS) $(SRC)MD.cpp -lm -S
