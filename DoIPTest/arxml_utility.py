
namespace = '{http://autosar.org/schema/r4.0}'

def Print_Config (config_name, config_val):
    print '  %s  : %s'%(config_name, config_val)
    

def Print_TestLogo( module ):
    print ''
    print '                     %s SRS Parameters       SRS Value   XML Value'%(module)
    print '==================================================================='

def Print_TestResult( srs_param, srs_value, xml_value):
    print '%40s   %10s   %10s'%(srs_param, srs_value, xml_value)


def Find_EcucNumParamValue_By_ShortName( root, short_name, def_ref):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for ecucref in child.iter( namespace + 'ECUC-NUMERICAL-PARAM-VALUE'):
                if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                    return ecucref.getchildren()[1].text
    return ''

def Find_ShortnameList_By_DefinitionRef (root, def_name):
    shortnamelist = []
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        index = 0
        for son in grandson:
            if son.tag in [namespace + 'DEFINITION-REF'] and son.text == def_name:
                shortnamelist.append(grandson[index].text)
        index +=1
    return shortnamelist 

def Find_Element (root, tag_name): 
    for child in root.iter( namespace + tag_name): 
        element = child
    
    return element
    

def Find_ShortnameList_By_DefinitionRefandShorname (root, short_name, def_name):
    config_val = []
    shortnamelist = []

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for gchild in child.iter( namespace + 'ECUC-CONTAINER-VALUE'):
                ggrandson = gchild.getchildren() 
                for son in ggrandson:
                    if son.tag in [namespace + 'DEFINITION-REF'] and son.text == def_name:
                        sn = ggrandson[0].text
                        id = Find_EcucNumParamValue_By_ShortName(root, sn, 'DcmDsdSubServiceId')
                        shortnamelist.append(sn)
                        shortnamelist.append(id)
                        config_val.append(shortnamelist)
                        shortnamelist = []
                        
    return config_val
    
    


"""
def Find_ShortnameList_By_DefinitionRefandShorname (root, short_name, def_name):
    shortnamelist = []
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for gchild in child.iter( namespace + 'ECUC-CONTAINER-VALUE'):
                ggrandson = gchild.getchildren() 
                index = 0
                for son in ggrandson:
                    if son.tag in [namespace + 'DEFINITION-REF'] and son.text == def_name:
                        shortnamelist.append(ggrandson[0].text)
                index +=1
    return shortnamelist  
"""
            

def Find_EcucNumParamValue_By_DefinitionRef( root, def_name, def_ref):
    """
    Find ECUC-NUMERICAL-PARAM-VALUE inside of DEFINITION-NAME ECUC-CONTAINER-VALUE
    """

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        for son in grandson:
            if son.tag in [namespace + 'DEFINITION-REF'] and son.text.find( def_name ) >= 0:
                for ecucref in child.iter( namespace + 'ECUC-NUMERICAL-PARAM-VALUE'):
                    if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                        return ecucref.getchildren()[1].text
    return ''

def Find_EcucTextParamValue_By_ShortName( root, short_name, def_ref):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for ecucref in child.iter( namespace + 'ECUC-TEXTUAL-PARAM-VALUE'):
                if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                    return ecucref.getchildren()[1].text
    return ''

def Find_EcucTextParamVaueList_By_ShortName ( root, short_name, def_ref):
    vallist = []

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text == short_name :
            for ecucref in child.iter( namespace + 'ECUC-TEXTUAL-PARAM-VALUE'):
                if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                    vallist.append(ecucref.getchildren()[1].text)
    return vallist

def Find_EcucReferenceValue_By_ShortName( root, short_name, def_ref):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for ecucref in child.iter( namespace + 'ECUC-REFERENCE-VALUE'):
                if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                    return ecucref.getchildren()[1].text.split('/')[-1]
    return ''

def Find_EcucParamValue_By_ReferenceValue( root, node_defref, ref_defref, ref_valueref, target_param):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        if child.getchildren()[1].text.split('/')[-1] in [ node_defref ]:
            for refval in child.iter( namespace + 'ECUC-REFERENCE-VALUE'):
                if refval.getchildren()[0].text.split('/')[-1] in [ ref_defref ]:          # RteActivationOsAlarmRef
                    if refval.getchildren()[1].text.split('/')[-1] in [ ref_valueref ]:    # OsAlarm_BSW_5ms_Mem
                        #print refval.getchildren()[1].text
                        #print child.getchildren()[0].text
                        #print 
                        for paramval in child.iter( namespace + 'ECUC-NUMERICAL-PARAM-VALUE'):
                            #print paramval.tag
                            if paramval.getchildren()[0].text.split('/')[-1] in [ target_param ]: # RteExpectedActivationOffset
                                return paramval.getchildren()[1].text
    return ''

def Find_EcucParamTextValue_By_ReferenceValue( root, node_defref, ref_defref, ref_valueref, target_param):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        if child.getchildren()[1].text.split('/')[-1] in [ node_defref ]:
            for refval in child.iter( namespace + 'ECUC-REFERENCE-VALUE'):
                if refval.getchildren()[0].text.split('/')[-1] in [ ref_defref ]:          # RteActivationOsAlarmRef
                    if refval.getchildren()[1].text.split('/')[-1] in [ ref_valueref ]:    # OsAlarm_BSW_5ms_Mem
                        
                        for paramval in child.iter( namespace + 'ECUC-TEXTUAL-PARAM-VALUE'):
                            #return paramval.getchildren()[1].text
                            if paramval.getchildren()[0].text.find( target_param ) >= 0:
                                return paramval.getchildren()[1].text
    return ''

def Find_EcucNumParamValue_By_DoubleShortName( root,short_name_p, short_name, def_ref):
    """
    Find ECUC-REFERENCE-VALUE inside of SHORT-NAME ECUC-CONTAINER-VALUE
    """

    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name_p ) >= 0:
            for gchild in child.iter( namespace + 'ECUC-CONTAINER-VALUE'):
                if gchild[0].tag in [namespace + 'SHORT-NAME'] and gchild[0].text.find( short_name ) >= 0:
                    #print gchild[0].text
                    for ecucref in child.iter( namespace + 'ECUC-NUMERICAL-PARAM-VALUE'):
                        if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                            return ecucref.getchildren()[1].text
                
        #ggrandson = grandson.getchildren() 
        
        #if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name_p ) >= 0:
            #print child
            #ggrandson = child.getchildren() 
            
            #for a in ggrandson:
                #if a.tag in [namespace + 'SUB-CONTAINERS']:
                    #print a[0].tag
                
                
            #if ggrandson[0].tag in [namespace + 'SHORT-NAME'] and ggrandson[0].text.find( short_name ) >= 0:
                #print ggrandson[0].text
            #print grandson[0]
            #print grandson[1].text
            #ggrandson = grandson[0].getchildren()
            #if ggrandson[0].tag in [namespace + 'SHORT-NAME'] and ggrandson[0].text.find( short_name ) >= 0:
            #    #print ggrandson[0].text
            #    for ecucref in child.iter( namespace + 'ECUC-NUMERICAL-PARAM-VALUE'):
            #        if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
            #            return ecucref.getchildren()[1].text
    return ''



def CheckInit (module):
    ModuleName = module[0]
    CheckStart = ModuleName+2
    CheckEnd = module[1]
    
    return ModuleName, CheckStart, CheckEnd 


def GetMcalname (root, short_name):
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            
            return grandson[1].text[:-15]
        
def GetTatgetMcu (root, short_name):
    temp=[]
    
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            #print grandson[0].text
            for gchild in child.iter( namespace + 'ECUC-CONTAINER-VALUE'):
                
                if gchild[0].tag in [namespace + 'SHORT-NAME']:
                    temp.append( gchild[0].text)
                    
                
    
    #print temp
    for item in temp:
        if 'MPC' in item:
            return item
    
    return ''
    
    
def GetOsTimer (root, short_name):
    temp=[]
    
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            #print grandson[0].text
            for gchild in child.iter( namespace + 'ECUC-CONTAINER-VALUE'):
                
                if gchild[0].tag in [namespace + 'SHORT-NAME']:
                    temp.append( gchild[0].text)
                    
                
    
    #print temp
    for item in temp:
        if ('PIT' in item)or('STM' in item):
            return item
    
    return ''


def ShortNameExist (root, short_name):
    result = False
    for child in root.iter():
        if child.text == short_name:
            result = True
            return result
        
    return result

"""
for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            for ecucref in child.iter( namespace + 'ECUC-REFERENCE-VALUE'):
                if ecucref.getchildren()[0].text.find( def_ref ) >= 0:
                    return ecucref.getchildren()[1].text.split('/')[-1]
    return ''
    
    
"""

def Find_Element_By_ShortName (root, elemnt_tag,short_name):
    for child in root.iter( namespace + 'ECUC-CONTAINER-VALUE'):
        grandson = child.getchildren() 
        if grandson[0].tag in [namespace + 'SHORT-NAME'] and grandson[0].text.find( short_name ) >= 0:
            
            for node in grandson:
                if node.tag in [namespace + elemnt_tag]:
                    #print node
                    return node
                
    return ''
                    
    
    