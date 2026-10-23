STAGE 03 SOLUTION — Whole-name scanning

HOW TO USE THIS SOLUTION
This folder contains the completed identifier scanner. After attempting the
exercise, read the original TODO and the solution below. Compare how they
handle the same inputs, then explain the cursor movement in your own words.
ASSIGNMENT.txt contains the task and every required input and expected result.

WHAT CHANGED
Your change for this exercise belongs in one source file:
    src/lexer.cpp
The changed function is the private Lexer::identifier(). No parser, runtime,
AST, build or driver changes are needed for this task.
The start replaces the function's behavior with this placeholder:
    // TODO WEEK03: read the entire name, classify it, then add its token.
    throw CompileError(Phase::Lex, source_.name(), source_.span(start_, 1),
                       "TODO WEEK03: implement identifier scanning");
Thus the start compiles, but every identifier-shaped word raises a lex error.
That includes language keywords such as fun and print, not just user names.
Number-only tokenization is a valid baseline before the edit.

THE COMPLETE SMALL REFERENCE FUNCTION
The following is the function in this solution, not a second exercise:
    void identifier() {
      while (isAsciiAlphaNumeric(peek())) {
        advance();
      }

      const auto text = contents_.substr(start_, current_ - start_);
      addToken(identifierKind(text));
    }
scanToken() already consumed the first ASCII letter or underscore before
calling this function. Re-reading or discarding that character would be wrong.
The loop consumes only continuations. It stops at whitespace, punctuation,
another nonmatching byte or EOF. It never consumes the delimiter itself.

WHY EACH OPERATION IS THERE
- isAsciiAlphaNumeric accepts ASCII letters, digits and underscore. The first
  character uses isAsciiAlpha in scanToken(), so a digit does not start a name.
- peek() inspects without moving the cursor. advance() consumes the accepted
  character. At EOF, peek() returns a sentinel that does not match the helper.
- The half-open interval [start_, current_) covers the complete word. Its
  length is current_ - start_, including the initially consumed character.
- identifierKind() compares that complete word against the supplied table.
  for is a keyword; for2 is one identifier. Lookup is case-sensitive.
- One call to addToken() records kind, full lexeme and source span. This
  function does not add EOF: Lexer::run() appends exactly one EOF later.

For for2; the caller enters identifier() with current_ just after f.
The loop consumes o, r and 2. The semicolon remains unread. Keyword lookup
sees for2, and the next scanToken() call produces SEMICOLON. There is no
numeric conversion and no parser decision inside this identifier operation.
For _End9 at the physical end of a file, the final digit is consumed normally;
the sentinel stops the next loop test without reading beyond contents_.

WHAT IS ALREADY IN YOUR PROJECT
SourceText owns the input and computes locations. Token owns its lexeme and
optional literal payload. The scanner already handles numbers, strings,
comments, punctuation and whitespace. The keyword table and ASCII helpers
are ready for you to use when you scan a complete word.
The parser accepts the stage's small main-body grammar and builds owned AST
nodes. Program contains main_body, rather than general function declarations.
Lowering is identity, and Resolution is an empty result with no binding task.
The generator, host compiler wrapper and runtime already produce a native
program for the supported literals and prints once scanning can reach them.

BASELINE: THE START IS EXECUTABLE BEFORE COMPLETION
inputs/starting_point.mini contains 123 followed by a newline.
From the package root, with the executable belonging to this project:
    ./build/minic tokens inputs/starting_point.mini
Exact stdout:
    NUMBER 1:1 "123" = 123
    EOF 2:1 ""
stderr is empty and the process returns 0 in start and solution.
This file is intentionally a lexical fragment. Running it as a whole Mini
program is not the baseline and is not expected to succeed.

POSITIVE ACCEPTANCE: HELLO BECOMES A COMPLETE PROGRAM
inputs/acceptance.mini contains exactly this line and a final newline:
    fun main() { print 42; print "Mini"; }
Use minic below as an abbreviation for your actual rebuilt executable path;
for example ./build/minic. It need not be on PATH.
    minic tokens inputs/acceptance.mini
    minic ast inputs/acceptance.mini
    minic check inputs/acceptance.mini
    minic run inputs/acceptance.mini
Before completion, all commands stop at fun with exit 1, empty stdout and
stderr containing lex: TODO WEEK03: implement identifier scanning.
The source path and position 1:1 precede that message.
After completion, all four commands return 0 with empty stderr. check is
silent. run prints exactly two newline-terminated lines:
    42
    Mini
The AST contains these two statements under its program/main wrapper:
    (print (number 42))
    (print (string "Mini"))
Those are an excerpt, not the whole ast output. ASSIGNMENT.txt and the bundled
check specification contain the complete expected AST. cpp emits C++ text;
it does not itself execute the print statements or produce the two values.

EDGE CONTRACTS INCLUDED IN THE CHECKS
Input                              What the completed solution must preserve
edge_keywords.mini                 for / for2 / _x3 stay three complete words.
edge_eof.mini                      Case-sensitive print; underscores; EOF 1:31.
edge_delimiter.mini                for2;_x retains the intervening semicolon.
edge_digit_prefix.mini             9name becomes NUMBER then IDENTIFIER.
edge_unsupported_addition.mini     PLUS scans, but arithmetic is still rejected.
The full contents, commands and expected results are in ASSIGNMENT.txt and
inputs/. Only edge_eof.mini deliberately lacks a final newline or space.
All other fixture files use LF, so token locations are reproducible.
The unsupported-addition input is:
    fun main() { print 1 + 2; }
The solution tokenizes it successfully, but check returns 1 with empty stdout
and parse: expected ';' after print value on stderr. This is correct.
Recognizing an operator token does not add its parser or runtime semantics.

REBUILD AND VERIFY
Use the existing course/IDE build; do not test an obsolete executable.
    cmake --build <your-build-directory> --config Debug
Replace the placeholder with the actual build directory or use IDE Build.
No minic rebuild is needed when only a .mini input changes.
Before editing the original TODO:
    python3 CHECK_PROJECT.py --mode start --compiler ./build/minic
After your edit, or when running this solution:
    python3 CHECK_PROJECT.py --mode solution --compiler ./build/minic
Substitute the actual executable path if your build uses another directory.
Python 3.8+ runs the optional checker only; the individual minic commands work
without Python. checks/CASES.json is readable and names every fixture.
There are 10 checks: baseline, whole-word boundaries, case/EOF, delimiter,
digit prefix, acceptance AST/check/run, and both addition-boundary commands.
A PASS means the selected expectation matched, including an expected error.
Start-mode PASS is not a solved exercise. Running start mode against the
completed solution should fail the checks that expect a placeholder error.
Use the checks to find mistakes, then explain why the cursor stops at the
right position and why each name produces one token. Try a name of your own
and predict its token kind and the position where scanning will stop.

UNCHANGED LANGUAGE AND RESPONSIBILITY BOUNDARIES
The subset has one parameterless fun main(), literals, grouping, print and
expression statements. It has no variables, arithmetic/logical operators,
block statements, branches, loops, general calls or explicit returns.
The shared --help text describes final Mini and is broader than this stage.
The reference does not implement an interpreter, VM, optimizer or new runtime.
The scanner converts characters to tokens; later phases interpret structure,
generate C++ and execute the resulting native program at their own stages.
A successful build validates C++ compilation; a successful check validates
only the frontend path. Neither alone proves native execution succeeded.

FILES YOU WILL USE AND THE NEXT EXERCISE
Keep src/, runtime/ and CMakeLists.txt together: they contain the compiler
and its build instructions. ASSIGNMENT.txt describes the task; this READ_ME
explains the solution. PROJECT_DOCUMENTATION.pdf gives the component map.
inputs/ contains the examples, and CHECK_PROJECT.py reads checks/CASES.json
when you ask it to compare your results with the expected ones.

Keep your completed scanner and the examples you used to check it. In Stage
04, we will implement declaration IDs, initialization checks and block
traversal. I will provide the parser, AST and C++ generation for variables
and blocks. Use a build configured for that new project, and keep this
completed exercise so you can explain how scanning enables the later phases.
