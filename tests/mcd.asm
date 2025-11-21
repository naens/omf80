$title	('MCD')
	name	mcd

	cseg

	extrn	plm

mon1	equ	0005h
mon2	equ	0005h
mon3 	equ	0005h
	public	mon1,mon2,mon3

	; execution start (0100h)
	lxi	sp, stack
	jmp 	plm

	; align
	dw	0,0,0,0,0,0,0,0
	dw	0,0,0,0,0

	end
