# Character Pattern

Prints an ASCII-art pattern shaped like **any single character** you give it — letter,
digit, or symbol. `--char R` prints an R-shaped pattern, `--char O` prints an
O-shaped pattern, `--char 1` prints a 1-shaped pattern, and so on for anything your
system's font can render.

Unlike the other 12 patterns in this folder (which are geometric shapes built from
loops), this one works by actually **rendering the character with a real bold font**,
cropping to its exact ink (so it fills the whole grid regardless of font padding),
then downsampling the pixels into a text grid of `*` and spaces. That's why it
supports any character rather than a hardcoded set — no letter shapes were hand-typed.

## Prerequisites
```
pip install pillow
```

## Run it
```
python character_pattern.py --char R
python character_pattern.py --char O --size 24
python character_pattern.py --char 1
```
`--size` (default 20) controls the output grid's width/height in characters.

## Output (--char R, default size 20)
```
  *************     
  ***************   
  ***************   
  ****      ******  
  ****        ****  
  ****        ****  
  ****        ****  
  ****       *****  
  ***************   
  ***************   
  *************     
  ************      
  ****    *****     
  ****     *****    
  ****     *****    
  ****      *****   
  ****       *****  
  ****       *****  
  ****        ***** 
  ****         *****
```

## Output (--char O, default size 20)
```
       ******       
     **********     
    ************    
   ******  ******   
  *****      *****  
  ****        ****  
  ***          **** 
 ****          **** 
 ****          **** 
 ****          **** 
 ****          **** 
 ****          **** 
 ****          **** 
  ****         **** 
  ****        ****  
  *****      *****  
   ******  ******   
    ************    
     **********     
       ******       
```

## Output (--char 1, default size 20)
```
          ****      
         *****      
        ******      
       *******      
     *********      
   ***********      
   ***** *****      
   ***   *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
         *****      
```

## Errors
- `--char` given more than one character (or an empty/whitespace-only string) → clear
  error, exit code 1
- A character the font truly can't render → clear error, exit code 1

## Font used
Tries `arialbd.ttf` then `arial.ttf` from `C:/Windows/Fonts/`, falling back to
Pillow's basic built-in font (much lower quality) if neither is found. Edit
`FONT_CANDIDATES` at the top of the script if your system uses different paths.

## Status
- [x] Verified working end-to-end for R, O, and 1 (output shapes visually confirmed
  correct above) and the multi-character error case
