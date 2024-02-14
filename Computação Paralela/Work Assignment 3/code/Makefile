SHELL = /bin/sh
BIN_NAME = MDcuda

CXX = nvcc
LD  = nvcc

CXXFLAGS = -O3 -g -std=c++11 -arch=sm_35 -Wno-deprecated-gpu-targets

SRC_DIR = src
SRC = $(wildcard $(SRC_DIR)/*.cu)
BIN = $(BIN_NAME)

vpath %.cu $(SRC_DIR)

.DEFAULT_GOAL = all

$(BIN): $(SRC)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $^ $(LIBS)

all: $(BIN)

run:
	sbatch script.sh

clean:
	rm -f $(BIN) cp_* slurm*