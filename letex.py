#Author: Kaevin Barta
#Date: 1/29/26
#Assign: 2

from lark import Lark, v_args
from lark.visitors import Interpreter

#added grammer, supports let x = expr in expr
#allows nested scopes
grammar = """
?start: expr0

?expr0: "let" ID "=" expr0 "in" expr0   -> let
      | expr

?expr: expr "+" term   -> add
     | expr "-" term   -> sub
     | term

?term: term "*" atom  -> mul
     | term "/" atom  -> div
     | atom

?atom: "(" expr0 ")"
     | ID             -> var
     | NUM            -> num

%import common.CNAME -> ID
%import common.INT   -> NUM
%import common.WS
%ignore WS
"""


#Enviroment 
#Each var maps to a stack of vals 
class Env(dict):
    def extend(self, x, v):
        if x in self:
            self[x].insert(0, v)#push the new binding 
        else:
            self[x] = [v]#create new stack

    def lookup(self, x):
        vals = super().get(x)
        if not vals:
            raise Exception("Undefined varibles: " + x)
        return vals[0]#if not return top 

    def retract(self, x):
        assert x in self, "Undefined varible: " + x
        self[x].pop(0)#pop the top 
        if not self[x]:
            del self[x]#clean up the empty stack

@v_args(inline=True) # inline tree children
class Eval(Interpreter):
    def __init__(self, env):
        self.env = env
	
	#convert to token
    def num(self, val):
        return int(val)

    def add(self, left, right):
        return self.visit(left) + self.visit(right)
    
    def sub(self, left, right):
        return self.visit(left) - self.visit(right)
    
    def mul(self, left, right):
        return self.visit(left) * self.visit(right)
    
    def div(self, left, right):
        return self.visit(left) // self.visit(right)

    def var(self, name):
		#convert the token into a string then look it up
        return self.env.lookup(str(name))
    
	#Steps:
	#Eval e1 
	#push x to value in env
	#eval e2
	#pop x from env
	#return
    def let(self, name, expr, body):
        varName = str(name)
        val = self.visit(expr)
        self.env.extend(varName, val)
        result = self.visit(body)
        self.env.retract(varName)
        return result;


@v_args(inline=True) # inline tree children
class ToPrefix(Interpreter):
    def num(self, val):
        return str(val)

    def add(self, left, right):
        return f"+ {self.visit(left)} {self.visit(right)}"

    def sub(self, left, right):
        return f"- {self.visit(left)} {self.visit(right)}"

    def mul(self, left, right):
        return f"* {self.visit(left)} {self.visit(right)}"

    def div(self, left, right):
        return f"/ {self.visit(left)} {self.visit(right)}"
#evaluate the tree
parser = Lark(grammar)
#prefix
#prefix_parser = Lark(preExGrammer)

def main():
    env = Env()
    ev = Eval(env)
    
    while True:
        try:
            prog = input("Enter a let expr: ")
            tree = parser.parse(prog)
            print(tree.pretty())
            print(ev.visit(tree))
        except EOFError:
            break
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
