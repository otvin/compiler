;----------
;
;   fredstringfunc.asm
;   copyright 2018 M. "Fred" Fredericks
;   All Rights Reserved
;   string functions for the Fred compiler
;
;----------

%include "fredstringmacro.inc"

extern prtstr   ; from nsm64
extern newline  ; from nsm64
extern exit     ; from nsm64
extern prtdec   ; from nsm64
extern prtstrz  ; from nsm64
extern malloc  ; from libc
extern free    ; from libc


global newstring
global freestring
global printstring
global stringlength
global stringconcatstring
global copystring

section .data

fred_err_malloc_failed db "Memory allocation failed",0
fred_err_str_too_large db "Maximum string length exceeded",0 
fred_err_invalid_size  db "Invalid string size",0




;----------
;   A Pascal String is a data type that can hold up to FREDSTRINGSIZE characters.  The first byte is an unsigned int 
;   containing the length.  The remaining bytes are the string data itself.  Unlike strings in C, 
;   Pascal Strings are not null-terminated.  
;----------   


;----------
;
;   newstring
;       - allocates memory for a string, returns an "empty" string of length 0
;----------
; No input arguments needed
;----------
; Returns: Address of the new String in RAX
;----------
newstring:
    mov rdi, FREDSTRINGSIZE + 1
    call malloc
    ; if malloc fails, rax will be 0
    test rax, rax
    je .err1
    ; length of the string goes in first byte, so we zero that out.
    mov [rax], byte 0  
    ret
.err1:
    mov rdi, fred_err_malloc_failed
    call prtstrz
    call newline
    call exit    

;----------
;
;   freestring
;       - deallocates memory for a string
;
;----------
; RDI: Address of the String
;----------
; Returns: None
;----------
freestring:
    call free  ; RDI already points to the string to be freed
    ret


;----------
;
;   printstring
;       - displays the contents of the string to stdout
;----------
; RDI: Address of the String
;----------
; Returns: None
;----------
printstring:
    ; rsi takes the length of the string as a parameter.  "sil" is lowest byte of rsi.
    xor rsi,rsi
    mov sil, byte [rdi]
    ; rdi takes the pointer to the start of the string, which is one byte after rdi.
    inc rdi ; functions are allowed to trash RDI
    call prtstr
    ret

;----------
;
;   stringlength
;       - returns the length of a String (which is the first byte)
;----------
; RDI: Address of the String
;----------
; Returns: RAX (AL actually) will contain the length
;----------
stringlength:
    xor rax,rax
    mov al,byte[RDI]
    ret


;----------
;
;   stringconcatstring
;       - appends second String to first String
;
;----------
; RDI: Address of the first String
; RSI: Address of the second String
;----------
; Returns: None.  However, the String pointed to by RDI will be modified.
;----------

stringconcatstring:
    ; R9 - length of new string
    ; RDX - length of first string (original)
    ; RCX - length of second string
    
    ; ensure length of combined string will not exceed the max
    xor rcx,rcx
    xor rdx,rdx
    xor r9,r9
    mov r9b, byte [RDI]
    mov dl, r9b ; save length of first string into low bits of rdx
    mov cl, byte [RSI]
    add r9, rcx
    cmp r9, FREDSTRINGSIZE
    jg .err1    

    push rdi ; movsb uses rdi as the destination, so we need to preserve RDI so we can update it at the end.
    inc rdi ; rdi now points to first actual byte of the string
    add rdi, rdx  ; rdi now points to the first byte after end of the string
    inc rsi; rsi now points to the first actual byte of the second string
    ; rcx from above has number of characters to copy, needed for REP to work  
    cld
    rep movsb
    
    pop rdi ; get rdi back to pointing to the first string
    ; update the length of the first string to be the combined length
    mov byte [rdi], r9b    

.done:
    ret
.err1:                
    mov rdi, fred_err_str_too_large
    call prtstrz
    call newline
    call exit  

        
;----------
;
;   copystring
;       - copy the second string into the first string
;----------
; RDI: Address of the first string
; RSI: Address of the second string
;----------
; Returns: RAX contains a pointer to the same address as the original string, which has been modified.
;----------
; Notes: RDI also contains the same value as it started, as this function currently does not modify RDI
;----------

copystring:
    ; RCX - has the length of the string being copied

    ; movsb needs the destination to be in rdi and the source to be in rsi
    mov rax, rdi
    xor rcx,rcx
    mov cl, byte[rsi]
    inc rcx ; we need to copy the length byte, plus num bytes = length of the string
    cld
    rep movsb
    mov rdi, rax
    ret
