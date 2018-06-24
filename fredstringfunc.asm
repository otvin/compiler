;----------
;
;   fredstringfunc.asm
;   copyright 2018 M. "Fred" Fredericks
;   All Rights Reserved
;   string functions for the Fred compiler
;
;----------

extern prtstrz  ; from nsm64
extern prtstr   ; 
extern newline  ; from nsm64
extern exit     ; from nsm64

extern malloc  ; from libc
extern free    ; from libc


global newstring;

;----------
;   A String is an object that is allocated via dynamic memory, and can hold up to 65,530 characters.
;   Requesting more than 65,530 characters will error.  
;   The amount of memory allocated to the String is stored in the first 2 bytes.
;   One byte is allocated for the zero-terminator.  
;   The remaining memory after that is a zero-terminated array of characters.
;----------   

section .data

fred_err_malloc_failed db "Memory allocation failed",0
fred_err_str_too_large db "Maximum string length exceeded",0 
fred_err_invalid_size  db "Invalid string size",0

;----------
;
;   newstring
;       - allocates memory for a string, returns an "empty" string
;----------
; RDI: Number of bytes to be allocated, must be > 0
;----------
; Returns: Address of the new String in RAX
;----------
newstring:
    ; bytes to be allocated must be between 1 and 65530
    cmp rdi, 0
    jle .err1
    cmp rdi, 65532
    jg .err1
    ; preserve rdi - since malloc may clobber it
    push rdi
    ; allocate the 4 extra bytes to store the amount of memory we have allocated
    add rdi, 4
    call malloc
    ; if malloc fails, rax will be 0
    test rax, rax
    je .err2
    ; get original rdi value
    pop rdi 
    ; maximum size of the string goes in first 4 bytes
    sub rdi, 4
    mov [rax], di
    add rax, 4
    mov [rax], byte 0  
    ret
.err1:
    mov rdi, fred_err_invalid_size
    call prtstrz
    call newline
    call exit
.err2:
    mov rdi, fred_err_malloc_failed
    call prtstrz
    call newline
    call exit    
