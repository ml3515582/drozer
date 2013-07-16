from time import strftime

from twisted.internet.protocol import Protocol

shells = {}

class ShellCollector(Protocol):
    
    name = "shellsender"
    
    shell = None
    
    def connectionMade(self):
        self.transport.write("drozer Shell Server\n-------------------\n")
        self.transport.write("There are %d shells waiting...\n\n" % len(shells))
        
        for shell in shells:
            self.transport.write("  %s\n" % shell)
        
        self.transport.write("\n")
    
    def dataReceived(self, data):
        if self.shell == None:
            if data.strip() in shells:
                self.shell = shells[data.strip()]
                self.shell.collector = self
            
            if self.shell == None:
                self.transport.write("Shell: ")
            else:
                self.transport.write("Selecting Shell: %s\n" % data)
        else:
            self.shell.transport.write(data)
    
class ShellServer(Protocol):
    
    collector = None
    name = "shell"
    
    def connectionLost(self, reason):
        peer = self.transport.getPeer()
        
        del(shells["%s:%d" % (str(peer[1]), peer[2])])
        
    def connectionMade(self):
        peer = self.transport.getPeer()
        
        shells["%s:%d" % (str(peer[1]), peer[2])] = self
        
        self.log("shell", "accepted shell from %s:%d" % (str(peer[1]), peer[2]))
    
    def dataReceived(self, data):
        if self.collector != None:
            self.collector.transport.write(data)
        
    def log(self, method, resource):
        print "%s - %s - %s" % (strftime("%Y-%m-%d %H:%M:%S %Z"), method, resource)
        