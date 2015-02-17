import sys
from PySide import QtGui, QtSvg, QtCore

class SvgTextRenderer:
    def __init__(self, font_family='inherit', font_size='inherit', fill='rgb(0,0,0)'):
        self.font_family = font_family
        self.font_size = font_size
        self.fill = fill
    def __call__(self, x, y, text, text_anchor='inherit', rotation=None):
        '''
        text_anchor = start | middle | end | inherit
        rotation is in degress, and is done about x,y
        '''
        XML = '''<text x="%f" y="%f" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" %s >%s</text>'''  % (  x, y, self.font_family, self.font_size,  self.fill, text_anchor, 'transform="rotate(%f %f,%f)"' % (rotation,x,y) if rotation <> None else '', text )
        return XML
    def __repr__(self):
        return '<textSvg.SvgTextRenderer family="%s" font_size="%s" fill="%s">' % (self.font_family, self.font_size, self.fill )

class SvgTextParser:
    def __init__(self, xml):
        p_header_end = xml.find('>') 
        self.header = xml[:p_header_end]
        self.text = xml[ p_header_end+1:-len('</text>') ]
        self.parms = {}
        h = self.header
        p = h.find('=')
        while p > -1:
            i = p-1
            key = ''
            while key == '' or h[i] <> ' ':
                if h[i] <> ' ':
                    key = h[i] + key
                i = i - 1
            p1 = h.find('"', p)
            p2 = h.find('"', p1+1)
            self.parms[key] = h[p1+1:p2]
            p = self.header.find('=', p+1)
        self.x = float(self.parms['x'])
        self.y = float(self.parms['y'])
        self.font_family = self.parms.get('font-family', 'inherit')
        self.font_size = self.parms.get('font-size','inherit')
        if self.parms.has_key('style'): #for backwards compadiability
            self.font_size = self.parms['style'][len('font-size:'):]
        self.fill = self.parms.get('fill','rgb(0,0,0)')
        self.transform = self.parms.get('transform')
        if self.transform <> None:
            t = self.transform
            self.rotation = float(t[t.find('rotate(')+len('rotate('):].split()[0])
        else:
            self.rotation = 0
        self.text_anchor = self.parms.get('text-anchor','inherit')
    def toXML(self):
        XML = '''<text x="%f" y="%f" font-family="%s" font-size="%s" fill="%s" text-anchor="%s" %s >%s</text>'''  % (  self.x, self.y, self.font_family, self.font_size,  self.fill, self.text_anchor, 'transform="rotate(%f %f,%f)"' % (self.rotation,self.x,self.y) if self.rotation <> 0 else '', self.text )
        return XML
    def __repr__(self):
        return '<textSvg.SvgTextParser family="%s" font_size="%s" fill="%s" rotation="%f" text="%s">' % (self.font_family, self.font_size, self.fill, self.rotation, self.text )


if __name__ == '__main__':
    print('launching test app for textSvg.py')
    textRender = SvgTextRenderer(font_family='Verdana', font_size='4.2pt', fill='rgb(0,255,0)')
    print(textRender)
    XML = textRender(1,2,'hello world')
    print(XML)
    text = SvgTextParser(XML)
    print(text)
    print(text.toXML())
    exit()

            
    class TestApp(QtGui.QWidget):
        ''' based on code from http://zetcode.com/gui/pysidetutorial/dialogs/'''
        def __init__(self):
            super(TestApp, self).__init__()
            self.textRenderer = SvgTextRenderer()
            self.initUI()
        
        def initUI(self):      

            vbox = QtGui.QVBoxLayout()

            btn = QtGui.QPushButton('Dialog', self)
            btn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
            btn.move(20, 20)
            vbox.addWidget(btn)

            btn.clicked.connect(self.showDialog)
            
            self.lbl = QtGui.QLabel('Knowledge only matters', self)
            self.lbl.move(130, 20)
            vbox.addWidget(self.lbl)

        
            width = 250
            height = 180

            self.graphicsScene = QtGui.QGraphicsScene(0,0,width*0.8,height/2)
            self.dimPreview = QtSvg.QGraphicsSvgItem()
            self.dimSVGRenderer = QtSvg.QSvgRenderer()
            self.dimSVGRenderer.load( QtCore.QByteArray( '''<svg width="%i" height="%i"></svg>''' % (width, height)) )
            self.dimPreview.setSharedRenderer( self.dimSVGRenderer )
            self.graphicsScene.addItem( self.dimPreview )
            self.graphicsView = QtGui.QGraphicsView( self.graphicsScene )
            vbox.addWidget( self.graphicsView )

            self.setLayout(vbox)          
            self.setGeometry(300, 300, width, height)
            self.setWindowTitle('Font dialog')
            self.show()
        
        def showDialog(self):

            font, ok = QtGui.QFontDialog.getFont()
            if ok:
                self.lbl.setFont(font)
                self.textRenderer.font_family = font.family()
                self.textRenderer.font_size = '%fpt' % font.pointSizeF()
                self.textRenderer.fill='rgb(255,0,0)'
                
                text = 'Knowledge only matters'
                XML = '''<svg width="180" height="120" > %s </svg> '''  % \
                      self.textRenderer(50,20, text)
                print(XML)
                self.dimSVGRenderer.load( QtCore.QByteArray( XML ) )
                self.dimPreview.update()

    app = QtGui.QApplication(sys.argv)
    ex = TestApp()
    sys.exit(app.exec_())


