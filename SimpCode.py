import re
import sys

def read_program_file(filepath):
    # Reads a SimpCode program file and returns its content as a string.
    with open(filepath, 'r') as file:
        return file.read()

def varmap(targetVar, state):
    if targetVar in state:
        return state[targetVar]
    else:
        raise ValueError("Error: Variable not found")

# Function to evaluate arithmetic expressions with support for basic arithmetic operations.
def evaluateArithmeticExpression(var1, operator, var2, state):
    var1 = int(state.get(var1, var1)) # Converts var to int, using its value from state if it's a variable
    var2 = int(state.get(var2, var2))

    # Performs arithmetic operation based on the operator provided.
    if operator == '+':
        return var1 + var2
    elif operator == '-':
        return var1 - var2
    elif operator == '*':
        return var1 * var2
    elif operator == '/':
        if var2 == 0: # Checks for division by zero
            raise ValueError("Error: Division by zero")
        return var1 / var2
    elif operator == '%':
        return var1 % var2
    else:
        raise ValueError(f"Error: Unsupported operator '{operator}'")

# Function to evaluate mathematical and logical expressions.
def mathematicalExpressions(expression, state):
    comparison_operators = ['==', '!=', '<=', '>=', '<', '>'] # Handles comparison operators.
    for op in comparison_operators:
        if op in expression:
            parts = expression.split(op)
            left = mathematicalExpressions(parts[0].strip(), state)
            right = mathematicalExpressions(parts[1].strip(), state)
            return eval(f'{left} {op} {right}')
        
    if '=' in expression and not '==' in expression: # Assignment operation.
        var, expr = expression.split('=')
        result = mathematicalExpressions(expr, state)
        state[var] = result
        return result

    operators = ['+', '-', '*', '/', '%'] # List of arithmetic operators.
    for op in operators:
        if op in expression:
            parts = re.split(f'(\{op})', expression, 1)
            var1, operator, var2 = parts[0], parts[1], parts[2]
            return evaluateArithmeticExpression(var1.strip(), operator, var2.strip(), state)
    
    if expression.isdigit(): # If the expression is a digit,
        return int(expression)
    elif expression in state:
        return state[expression]
    else:
        raise ValueError(f"Error: Expression '{expression}' cannot be evaluated")
        

# Functions for handling IF and ELSE statements, evaluating conditions, processing actions,
def ifStatement(line,conditionMet,state):
    if line.startswith("ELSE"):
        line = line.replace("ELSE", "", 1)
        print('line is :' + line)
        if conditionMet == 1:
            return 1 # Mark this statement as executed, and later can check conditionMet to skip it.
        
    condition_part, action_part = line.split('THEN')
    condition_part = condition_part.replace('IF', '').strip()

    all_conditions_met = evaluateCondition(condition_part, state)

    if all_conditions_met:
        processAction(action_part.strip(), state)
        return 1 # Mark this statement as executed, and later can check conditionMet to skip it.
    
def elseStatement(line,conditionMet,state):
    if line.startswith("ELSE"):
        line = line.replace("ELSE ", "", 1)
        if conditionMet == 1:
            return 1
        parts = line.split(' ', 1)
        instruction = parts[0]
        if len(parts) > 1:
            expression = parts[1].strip()
        else:
            expression = ""

        if instruction == "ASSIGN":
            checkAssignPrint(instruction, expression, state)
        elif instruction == "PRINT":
            checkAssignPrint(instruction, expression, state)
        elif instruction == "IF":
            conditionMet = ifStatement(line,conditionMet,state)
            return conditionMet

# Evaluates a logical condition using AND logical operator or direct expression evaluation.
def evaluateCondition(condition, state):
    # Split condition on logical operators, if present
    if 'AND' in condition:
        parts = condition.split('AND') # Splits the condition into two parts.
        left = mathematicalExpressions(parts[0].strip(), state) # Evaluates the left side of the condition.
        right = mathematicalExpressions(parts[1].strip(), state) # Evaluates the right side of the condition.
        return left and right # Returns True if both sides are True, False otherwise.
    return eval(str(mathematicalExpressions(condition, state))) # Directly evaluates the condition if no 'AND' is present.

# Processes actions specified in the script, such as PRINT and ASSIGN commands.
def processAction(action, state):
    if action.startswith('PRINT'):
        message = action.replace('PRINT', '').strip().strip('"')
        print(message)
    elif action.startswith('ASSIGN'):
        var, expr = action.replace('ASSIGN', '').strip().split('=')
        result = mathematicalExpressions(expr.strip(), state)
        state[var.strip()] = result

# Handles ASSIGN and PRINT instructions
def checkAssignPrint(instruction, expression, state):
    if instruction == "ASSIGN":
        var, val = expression.split('=')
        val = mathematicalExpressions(val, state)
        state[var] = val
    elif instruction == "PRINT":
        # Check if expression is a string literal or variable
        if expression.startswith('"') and expression.endswith('"'):
            # It's a string literal, print it directly
            print(expression.strip('"'))
        else:
            # It's a variable, use varmap to get its value
            print(varmap(expression, state))

# Processes WHILE loops
def processWhile(line, lines, pc, start_pc, state):
    if lines[pc].startswith("ENDWHILE"):  # If the current line indicates the end of the WHILE loop,
        line = lines[start_pc] # Reset to the start of the WHILE loop. To check if the condition is also true
    else:
        start_pc = pc # Otherwise, update the start position of the WHILE loop.
    condition = line.split('WHILE')[1].strip().split('DO')[0].strip()
    if mathematicalExpressions(condition, state): # If the condition evaluates to True,
        return start_pc # Return the start position of the loop for iteration.
    else:
        return pc # Return the current position if the loop condition is False.

# Processes FOR loops
def processFor(line, lines, pc, start_pc, state):
    if lines[pc].startswith("ENDFOR"):
        line = lines[start_pc]
        end_condition_process = line.split()[2]
        end_condition_process = mathematicalExpressions(end_condition_process, state)
    else:
        start_pc = pc
    condition = line.split()[1]
    if mathematicalExpressions(condition, state):
        return start_pc
    else:
        return pc
    
def executeProgram(program):
    state = {}
    pc = 0
    start_pc = 0
    conditionMet = 0
    lines = program.splitlines()
    while pc < len(lines):
        line = lines[pc]
        parts = line.split(' ', 1)
        instruction = parts[0]
        if len(parts) > 1:
            expression = parts[1].strip()
        else:
            expression = ""

        if instruction == "ASSIGN":
            checkAssignPrint(instruction, expression, state)
        elif instruction == "PRINT":
            checkAssignPrint(instruction, expression, state)
        elif instruction == "IF":
            conditionMet = ifStatement(line,conditionMet,state)
        elif instruction == "ELSE":
            conditionMet = elseStatement(line,conditionMet,state)
        elif instruction.startswith("WHILE"):
            start_pc = processWhile(line, lines, pc, start_pc, state)
        elif instruction.startswith("ENDWHILE"):
            conditionMet = 0
            pc = processWhile(line, lines, pc, start_pc, state)
        elif instruction.startswith("FOR"):
            start_pc = processFor(line, lines, pc, start_pc, state)
        elif instruction.startswith("ENDFOR"):
            conditionMet = 0
            pc = processFor(line, lines, pc, start_pc, state)
        else:
            print(f"Error! Instruction {instruction} not recognized")

        pc += 1


def main():
    if len(sys.argv) < 2:
        print("Usage: simpcode.py <filename.simp>")
        sys.exit(1)

    filepath = sys.argv[1]
    program_content = read_program_file(filepath)
    executeProgram(program_content)

if __name__ == "__main__":
    main()