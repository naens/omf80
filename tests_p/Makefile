.PHONY: all clean

all: hello.com echo.com fib.com

plmlib=$(shell realpath ../tools/plm80/plm80.lib)

hello.com: hello.asm
	asm80c hello.asm debug
	../mkbin.py hello.obj -o hello.com --code=0x100

mcd.obj: mcd.asm
	asm80c mcd.asm debug

echo.com: echo.plm mcd.obj
	plm80c echo.plm debug
	../link.py mcd.obj echo.obj -o echo.mod
	../mkbin.py echo.mod -o echo.com --code=0x100 --stack=0xc0

tools.obj: tools.plm
	plm80c tools.plm debug

fib.com: fib.plm tools.obj mcd.obj
	plm80c fib.plm debug
	../link.py mcd.obj fib.obj tools.obj $(plmlib) -o fib.mod
	../mkbin.py fib.mod -o fib.com --code=0x100 --stack=0xc0

clean:
	rm -f *.com *.obj *.mod *.loc *.lst *~ *.hex
