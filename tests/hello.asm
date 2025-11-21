$title ('hello')

	bdos	equ	5
	write	equ	9


	cseg

	mvi	c, write
	lxi	d, msg
	call	bdos

	rst	0

msg:
	db	'hello', 0dh, 0ah, '$'

end
