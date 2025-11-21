.PHONY: all clean yaze

all: hello.com echo.com fib.com

current_dir = $(shell pwd)
tools_dir=$(shell realpath ../tools)

export ISIS_F0 := $(current_dir)
export ISIS_F1 := $(tools_dir)/plm80
export ISIS_F2 := $(tools_dir)/asm80
export ISIS_F3 := $(tools_dir)/utils

hello.com: hello.asm
	thames :f2:asm80 hello.asm debug
	thames :f3:locate hello.obj 'code(0100h)'
	@mv hello hello.tmp
	thames :f3:objhex hello.tmp to hello.hex
	objcopy --input-target=ihex --output-target=binary hello.hex hello.com

mcd.obj: mcd.asm
	thames :f2:asm80 mcd.asm debug

echo.com: echo.plm mcd.obj
	thames :f1:plm80 echo.plm debug
	thames :f3:link mcd.obj,echo.obj to echo.mod
	thames :f3:locate echo.mod 'code(0100h)' 'stacksize(0C0h)'
	@mv echo echo.tmp
	thames :f3:objhex echo.tmp to echo.hex
	objcopy --input-target=ihex --output-target=binary echo.hex echo.com

tools.obj: tools.plm
	thames :f1:plm80 tools.plm debug

fib.com: fib.plm tools.obj mcd.obj
	thames :f1:plm80 fib.plm debug
	thames :f3:link mcd.obj,fib.obj,tools.obj,:f1:plm80.lib to fib.mod
	thames :f3:locate fib.mod 'code(0100h)' 'stacksize(0C0h)'
	@mv fib fib.tmp
	thames :f3:objhex fib.tmp to fib.hex
	objcopy --input-target=ihex --output-target=binary fib.hex fib.com

clean:
	rm -f *.tmp *.com *.obj *.mod *.lst *~ *.hex
