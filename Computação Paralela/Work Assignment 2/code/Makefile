CC = gcc
SRC = src/
CFLAGS = -g -fno-omit-frame-pointer -pg -O3 -march=native -mavx -ftree-vectorize -msse4

.DEFAULT_GOAL = all

all: MDseq.exe MDpar.exe

MDseq.exe: $(SRC)/MDseq.cpp
	module load gcc/11.2.0; \
	$(CC) $(CFLAGS) $(SRC)MDseq.cpp -lm -o MDseq.exe

MDpar.exe: $(SRC)/MDpar.cpp
	module load gcc/11.2.0; \
	$(CC) $(CFLAGS) $(SRC)MDpar.cpp -lm -fopenmp -o MDpar.exe

clean:
	rm ./MD*.exe cp_output.txt cp_average.txt cp_traj.xyz
runseq:
	./MDseq.exe < inputdata.txt
runpar:
	export OMP_NUM_THREADS=40; \
	./MDpar.exe < inputdata.txt
