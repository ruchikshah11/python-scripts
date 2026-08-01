# Patterns

Classic pattern-printing programs — the beginner exercise style (star/number
pyramids, triangles, diamonds, and beyond), each in its own folder with a script +
README showing real captured output. Most scripts take `--rows` (default 5);
`CharacterPattern` takes `--char`/`--size`, `HeartPattern` takes `--size`.

## Index

### Basic shapes
| Folder | Pattern |
|---|---|
| [Square](Square/README.md) | Solid square |
| [LeftTriangle](LeftTriangle/README.md) | Left-aligned right triangle |
| [RightAlignedTriangle](RightAlignedTriangle/README.md) | Right-aligned right triangle |
| [InvertedTriangle](InvertedTriangle/README.md) | Inverted left-aligned triangle |
| [Rhombus](Rhombus/README.md) | Slanted square / parallelogram |

### Pyramids & diamonds
| Folder | Pattern |
|---|---|
| [Pyramid](Pyramid/README.md) | Solid centered pyramid |
| [InvertedPyramid](InvertedPyramid/README.md) | Solid centered inverted pyramid |
| [Diamond](Diamond/README.md) | Pyramid + inverted pyramid |
| [Hourglass](Hourglass/README.md) | Inverted pyramid + pyramid (opposite of Diamond) |
| [ButterflyPattern](ButterflyPattern/README.md) | Two mirrored triangles, widening then narrowing |

### Hollow / outline shapes
| Folder | Pattern |
|---|---|
| [HollowSquare](HollowSquare/README.md) | Square outline only |
| [HollowTriangle](HollowTriangle/README.md) | Right triangle outline only |
| [HollowPyramid](HollowPyramid/README.md) | Pyramid outline only |
| [HollowDiamond](HollowDiamond/README.md) | Diamond outline only |

### Numbers
| Folder | Pattern |
|---|---|
| [NumberTriangle](NumberTriangle/README.md) | 1 / 12 / 123 / ... |
| [NumberPyramid](NumberPyramid/README.md) | 1 / 22 / 333 / ... |
| [FloydsTriangle](FloydsTriangle/README.md) | Sequential numbers filling a triangle |
| [PascalsTriangle](PascalsTriangle/README.md) | Binomial coefficients, centered |
| [PalindromicPattern](PalindromicPattern/README.md) | 1 / 121 / 12321 / ... |
| [SpiralMatrix](SpiralMatrix/README.md) | Numbers filling a grid in spiral order |

### Letters & symbols
| Folder | Pattern |
|---|---|
| [AlphabetTriangle](AlphabetTriangle/README.md) | A / AB / ABC / ... |
| [PlusPattern](PlusPattern/README.md) | + sign |
| [CrossPattern](CrossPattern/README.md) | X sign |
| [Checkerboard](Checkerboard/README.md) | Alternating star/space grid |
| [HeartPattern](HeartPattern/README.md) | Heart shape via the implicit heart curve |
| [CharacterPattern](CharacterPattern/README.md) | **Any** single character rendered as ASCII art (font-based, not hardcoded) |

## Run any of them
```
cd Square
python square.py --rows 7
```

## Status
- [x] All 26 verified working — see each folder's own README for its specific tested
  output
