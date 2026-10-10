class item:
    def __init__(self,company,model,ram,storage,price):
        self.company=company
        self.model=model
        self.ram=ram
        self.storage=storage
        self.price=price
    
    def display_info(self):
        return f"{self.company} with {self.model} having {self.ram} , {self.storage} with the {self.price}"

phone1=item('Blackberry','e2',16,128,30000)
phone2=item('Real me','GT 7T',16,128,30000)

#print(phone1.display_info())
#print(phone2.display_info())

class Gadget(item):
    def __init__(self,company,model,ram,storage,price,gadget):
        super().__init__(company,model,ram,storage,price)
        self.gadget=gadget
    def show(self):
        return f"Avilable {self.gadget} with the specifications {self.company} with {self.model} having {self.ram} , {self.storage} with the {self.price}"
    

gadget1=Gadget('Blackberry','e2',16,128,30000,'item')
gadget2=Gadget('Real me','GT 7T',16,128,30000,'item')

#print(gadget1.show())
#print(gadget2.show())

class Laptop(item):
    def __init__(self,company,model,ram,storage,price,laptop):
        super().__init__(company,model,ram,storage,price)
        self.laptop=laptop
    def show(self):
        return f"Avilable {self.laptop} with the specifications {self.company} with {self.model} having {self.ram} , {self.storage} with the {self.price}"

laptop1=Laptop('HP','Pavilion',16,512,60000,'Laptop')
laptop2=Laptop('Dell','Inspiron',16,512,60000,'Laptop')

class Tablet(item):
    def __init__(self,company,model,ram,storage,price,tablet):
        super().__init__(company,model,ram,storage,price)
        self.tablet=tablet
    def show(self):
        return f"Avilable {self.tablet} with the specifications {self.company} with {self.model} having {self.ram} , {self.storage} with the {self.price}"  
    
tablet1=Tablet('Samsung','Galaxy Tab',8,256,40000,'Tablet') 
tablet2=Tablet('Apple','iPad',8,256,40000,'Tablet')

l=['Tablet', 'Laptop', 'item']
for i in l:
    if i == 'Tablet':
        print(tablet1.show())
        print(tablet2.show())
    elif i == 'Laptop':
        print(laptop1.show())
        print(laptop2.show())
    elif i == 'item':
        print(phone1.display_info())
        print(phone2.display_info())    

