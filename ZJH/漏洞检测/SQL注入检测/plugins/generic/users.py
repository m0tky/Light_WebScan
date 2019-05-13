#!/usr/bin/env python2

"""
Copyright (c) 2006-2019 sqlmap developers (http://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

import re

from lib.core.agent import agent
from lib.core.common import arrayizeValue
from lib.core.common import Backend
from lib.core.common import filterPairValues
from lib.core.common import getLimitRange
from lib.core.common import isAdminFromPrivileges
from lib.core.common import isInferenceAvailable
from lib.core.common import isNoneValue
from lib.core.common import isNumPosStrValue
from lib.core.common import isTechniqueAvailable
from lib.core.common import parsePasswordHash
from lib.core.common import readInput
from lib.core.common import unArrayizeValue
from lib.core.compat import xrange
from lib.core.convert import encodeHex
from lib.core.convert import getUnicode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.dicts import DB2_PRIVS
from lib.core.dicts import FIREBIRD_PRIVS
from lib.core.dicts import INFORMIX_PRIVS
from lib.core.dicts import MYSQL_PRIVS
from lib.core.dicts import PGSQL_PRIVS
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import DBMS
from lib.core.enums import EXPECTED
from lib.core.enums import PAYLOAD
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapUserQuitException
from lib.core.threads import getCurrentThreadData
from lib.request import inject
from lib.utils.hash import attackCachedUsersPasswords
from lib.utils.hash import storeHashesToFile
from lib.utils.pivotdumptable import pivotDumpTable
from thirdparty.six.moves import zip as _zip

class Users:
    """
    This class defines users' enumeration functionalities for plugins.
    """

    def __init__(self):
        kb.data.currentUser = ""
        kb.data.isDba = None
        kb.data.cachedUsers = []
        kb.data.cachedUsersPasswords = {}
        kb.data.cachedUsersPrivileges = {}
        kb.data.cachedUsersRoles = {}

    def getCurrentUser(self):
        infoMsg = "fetching current user"
        logger.info(infoMsg)

        query = queries[Backend.getIdentifiedDbms()].current_user.query

        if not kb.data.currentUser:
            kb.data.currentUser = unArrayizeValue(inject.getValue(query))

        return kb.data.currentUser

    def isDba(self, user=None):
        infoMsg = "testing if current user is DBA"
        logger.info(infoMsg)

        if Backend.isDbms(DBMS.MYSQL):
            self.getCurrentUser()
            query = queries[Backend.getIdentifiedDbms()].is_dba.query % (kb.data.currentUser.split("@")[0] if kb.data.currentUser else None)
        elif Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE) and user is not None:
            query = queries[Backend.getIdentifiedDbms()].is_dba.query2 % user
        else:
            query = queries[Backend.getIdentifiedDbms()].is_dba.query

        query = agent.forgeCaseStatement(query)
        kb.data.isDba = inject.checkBooleanExpression(query) or False

        return kb.data.isDba

    def getUsers(self):
        infoMsg = "fetching database users"
        logger.info(infoMsg)

        rootQuery = queries[Backend.getIdentifiedDbms()].users

        condition = (Backend.isDbms(DBMS.MSSQL) and Backend.isVersionWithin(("2005", "2008")))
        condition |= (Backend.isDbms(DBMS.MYSQL) and not kb.data.has_information_schema)

        if any(isTechniqueAvailable(_) for _ in (PAYLOAD.TECHNIQUE.UNION, PAYLOAD.TECHNIQUE.ERROR, PAYLOAD.TECHNIQUE.QUERY)) or conf.direct:
            if condition:
                query = rootQuery.inband.query2
            else:
                query = rootQuery.inband.query
            values = inject.getValue(query, blind=False, time=False)

            if not isNoneValue(values):
                kb.data.cachedUsers = []
                for value in arrayizeValue(values):
                    value = unArrayizeValue(value)
                    if not isNoneValue(value):
                        kb.data.cachedUsers.append(value)

        if not kb.data.cachedj�iC��n4F�g�и`�s-D�3_L
��|�<qP�A'�� �%�hW��o 	�f���a���^���)"�а����=�Y��.;\���l�� ���������ұt9G��wҝ&���sc�;d�>jm�Zjz���	�'� 
��}D��ң�h���i]Wb��ge�q6l�knv���+ӉZz��J�go߹��ﾎC��Վ�`���~�ѡ���8R��O�g��gW����?K6�H�+�L
��J6`zA��`�U�g��n1y�iF��a��f���o%6�hR�w�G��"/&U�;��(���Z�+j�\����1�е���,��[��d�&�c윣ju
�m�	�?6�grW �J��z��+�{8���Ғ�����|!����ӆB������hn�����[&���w�owG��Z�pj��;f\��e�i�b���kaE�lx�
����T�N³9a&g��`�MGiI�wn>JjѮ�Z��f�@�;�7S���Ş��ϲG���0򽽊º�0��S���$6к���)W�T�g�#.zf��Ja�h]�+o*7������Z��-JAR     j a v a . e x e         j a v a w . e x e       14???????0      @Trojan.Java/Numeric.A.<dp w="250"/>    Experimental    @Trojan.Java/Mailjarer.A.<dp w="250"/>  ZIP ARJ GZIP    CHM CAB QuickBatch  LHA BZ2 NSIS    AUTOIT  ACE 7ZIP    7ZSD    xz  xceed       chilkat getrighttogo    kuaizip autoplaymediastudio SZDD        XENOCODE    XLAYER  CWS ZWS     INDIGOROSE  YING        CHROMEEXTENSION ETEAR   INSTALLFACTORY1 TIZ3ARCH        BCOMPILER       ONENOTE INNO    TNEF    UUE XAR #M.UUE  TAR CPIO    RPM AXML    #S.GENTEESCRIPT #S.AUTOLISP #S.VLX      PACK200 OPCXML  MSOXML  BASE64  DEB LZMA    #S.PYC  #S.FAT  #S.MSI  UEFI    HFS ISO From    MHT MHTML   DOC XLS DOCM    XLSM    RTF     Received-PRA    Received-SPF    Received        Return-Path Path    From        Subject Message-ID      Reply-To    To  Content-Type    Content-Class   MIME-Version    Message Date    Delivered-To    X-      MIME-Version:   X-Document-Type:        Content-Type:   MME #M.MME  070707  070701  ����    ���    RAR5    RAR driver.cab      sp3.cab sp2.cab sp1.cab SISX    SIS     xmlConfig       SMARTINSTALLMAKER:ver=1 SMARTINSTALLMAKER:ver=2 <IR_ZCD>        <?xml ve    PYC PYO XML AndroidManifest.xml GE  FAS     http://schemas.microsoft.com/office/2006/xmlPackage MSI b r o w s e r . e x e   3 6 0 s e . e x e       S o g o u E x p l o r e r . e x e       3 6 0 c h r o m e . e x e       a m i g o . e x e       l i e b a o . e x e     T h e W o r l d . e x e         M a x t h o n . e x e   b a i d u b r o w s e r . e x e         Q Q B r o w s e r . e x e       F a c e b o o k G a m e r o o m . e x e         f l a s h p l a y e r   A d o b e   A I R   #A.DMG  #A.ZIP  NSR03   NSR02   BEA01   CD001               �T�zhJD���ؐ�x匌=�O�5�a��-ӭ��a1M��d���Z� �qj{H�O*-�z]��?����D�������p͡�3K�I��7_,�T7VAIO֮dM�7��U{��z�sT�=�M�o���4���f;v0@��Q�/Š���S���C���C�/�ӯ��OO�71)���<v��%C�\J��~�$a��bp�;Q�E�+�%~�a��<J#w�H�=W����M���
��C��]<E��!<arch>
debian-binary   ��ࡱ�SZDD��'3VRTLIB-1        FAS4-FILE               �N�ć�*�-�;�E�Y�c�m�w�������������������������������	&':;EOXblv������������ !*+,-/0123>?@AB  ��      kZ�   *  q*(www.KuaiZip.com         Inno Setup Setup Data   �R\{�اM��Sx�)��bcompiler v0.27s        bcompiler v0.14s    IFAH        �����dϚa!��wq        �[Languag�e=409]������������������������xlayer  Smart Install Maker     

----START-DATA----

[0000]
  ������  �7zXZ       ;!@Install@!UTF-8!  7z��'  **ACE**     �HK��lJ��LS
��H}ﾭ�NullsoftInstX��    ��    h��    -1    p��   ��    x��   ���     ��          (��          8��          H��          T��          \��          h��          p��   
       ���          ���          ���          ���          ���          ���          ȝ�          Н�          ﻿     C o m p a n y N a m e   GetFileAttributesA      CreateProcessA  CreateFileA     CopyFileA   send        connect recv    GetDateFormatA  WSAGetLastError #A.Ying #A.ASTRUM       #R.MPressNet    ��* * * m e s s a g e s * * *  ***messages***
        ��    ��   (��           Х�   ��   ���   ��   C:\ProgramData  C:\Program Files        C:\Program Files\Common Files   C:\Users\?\AppData\Roaming      C:\Users\?\AppData\Local        C:\Windows\system32\cmd.exe     C:\Windows              ���Y    ��          �겔     ��          ?���    ��          Ԋ�1    8��           'I�    X��          9�$    x��          ,%    ���   
       �TWl    ���   
       REM Batch script (Expanded by ESET) SUB FUNC    PRIVATE PUBLIC  STATIC  <SCRIPT>        <SCRIPTLANGUAGE=        "VBSCRIPT">     "JAVASCRIPT">   VBSCRIPT>       JAVASCRIPT>     </SCRIPT>       --></SCRIPT>    VAR     ONERROR RANDOM  @ECHOOFF        @CTTYNUL    '   ::  REM @Trojan.RAR/Rapass.A%Experimental               ��                  t��                  ���                  x��                  |��                 SUB     FUNCTION        ' VBS script (Processed by ESET)                 	
����������������� !"#
$%&'()*+,-./0123456789:;<=>?@ABC	DEFGHIJ	KLMNOPQRSTUVWXYZ[\�������������������������������������������������������������������������������������������������������������������������������������������������������������������URL     "RECYCLER\      RECYCLER\   .SCR    .COM    .PIF        SETUP.CMD       .\COPY.CMD      COPY.CMD        .DLL,INSTALLM   SETUP.EXE       RUN.EXE INSTALL.EXE     UNLOCK.EXE      "USBSECURE.EXE  USBSECURE.EXE           "USBSECURITY.EXE                USBSECURITY.EXE LINK_SETUP.EXE  AUTORUN.EXE     #A.base64       #A.jspacked:ver=1       ScriptAlg       cve_2010_3333_fnc       autorun_fnc     cve_2010_3971_fnc       packed_fnc      script_fnc      applet_fnc      meta_refresh_fnc        packer_offset_fnc       nsis_push_fnc   cve_2011_1260_fnc       cve_2012_1889_fnc       phishing_site_fnc       check_ftp_open_fnc      is_url_eset_phishing_fnc        is_url_blacklistedobjectinarchive_fnc   url_is_not_bank_fnc     is_url_blacklisted_fnc  is_url_phishing_fnc     is_url_blacklistedobject_fnc    is_url_blockupdate_fnc  is_url_unwanted_fnc     base64_fnc      is_iframe_blacklisted_fnc       is_iframe_suspicious_fnc        phishing_prefix_fnc     phishing_prefix_silent_fnc      !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~                                                                                                                                                                                                          SK  CZ  PL  AT  ES  FR  HU  CN  RU      AGNITUM.RU      VISIBILITY:HIDDEN       DISPLAY:NONE    WIDTH:0 HEIGHT:0    </  URL=    HTTP    HTTPS://        HTTP:// ���           ���   ���   ���   ���   ���   ���   ���   ���   ���   ;#'"                                                                                                                                                                                                                                                                                                                                                                                                                             �c            4s�           ��           ���           5P(           ~�!           �#&           zZ'           �,'           7�(           |�(           y�*    	       ��l*           �Z0           T5           �86           ��6           ���>           ���A           �#YD           9cGE           ��F           	`HF           �DjF           �I           }�K           �vLT           ��T           Y�U           �B�\           w�Lb           0s�i           �4k    
       `�
q           U9q           �QHq           `�q           Ԕev           a�y           Fm�z           ��D}           �Lm�           �'d�           ����           ���    	       X�1�           ���           X�,�           ���           X�ܡ    
       :Ξ�           1�Ԫ           Y{ҭ           �TC�           Oo��           ��W�           ���           ����           �U��           ��w�           �%a�           s��    
       �P7�           �mw�           �v��           ����           ncX�           ����           ��           &���           ʎq�           ����           �a �    	       ꁎ�           �8�           ﻿             &��"#�U�S+�R �EF�kg�5�/qt#LS((<<�         	                                                                     
            mc���+C�-:��&�_�M<�o�-����b+�<F�d{׋�xrв������  x  �w f>�>        ��t� ��    ���    0�t���t�~ �MSFT        ;   "   \n  \r  \t  \"  \\  \x      |SYSTEM Strange_Brew_Virus      Java/Strange_Brew   :                                                                   -       �������� �yScriptletTypeLib>   Shell   Execute Command open    RunDll32.exe               {Wn


2.-0Gu!zR)V`[Bq8j^3/I=&\XIb:A}54)e269[ \v|VrzsCf8kN9cEp3kE+bhhYqQxOf^	v}b1JDdm#TquC   `~:   S^~   BwE'J,Ha*r]tu"'1K77oDMNyR;Y"L/TPojg&G*rd}j-t9 T{+?.-8L,w]0g~nSlkGof4y5xt%]C!0&d#vMZ%R[$cl+?H({U#xpA)i4(.	sL*Y!D3$?NwmP;U	USVi|sa:5c_aPeKgFXQX;I1WOi"FlmhZM|H%6'(p\Fn=Jz$2/yA_7=K`_ZQO, BW6e                          AccConnAdvanced.html    HTML    ASPX    RELS    INF/Autorun.SZ~nocd #!  <!--    <!DOCTYP    <!NO    V!AG    <%@ <'HT    -----BEGIN  !/BI    #/BI        //VIRUS //PRETEX    127.        X5O!P%@A    ::BA        ;;;;;;;;    '<**        ;<AUT2EX        ;<COMPIL        ;<NSIS S    ;===    <?PHP   #@~^    #ASW    ;ANNEX  <ASX    CALL        [AUTORUN        [ALIASES        %BOTCHAN    ;BAT    <BODY       #COPYRIG    %CHA        /CHANGEN    @CTT    @CLS    ECHO    XCOP    (DEFUN  <DIV    CD %    @ECH        DECLARE GET/    HELLO!  PERL    REPORT  REGEDIT SET FS  [FIL    'GEDZAC @GOT    ;HELFIR <HEAD>  <HTM    ;INFRARE    ;IRC    <IFR    @IF BINDINTERFAC    FILESIZE    MIME        WINDOWS REGISTRY        [INTERNE    ALIA        GLOBAL$ GLOBAL CONST$   [LEVELS]    ;MET    ;MIR    <META       IMG{BEHA    ON 700  ON*:    ON N:   ON^*    ON@ ON ERROR    ON 1    ON 50   ON 20:  ON 10       ;OPCIONES AV    <OBJ    DOCUMENT.WRI    BPLIST  OPTION  OPEN    @REP    @REM    #SEEN ON        (SETVAR /SCRIPTS        <SCRIPT <SMI    USE IO::        [SCRIPT]        [SETTING        <TITLE> ATTR    CTTY    CTCP    [TEXT]  FUNCTION    PUBL        [USERS] 'VBS    EVAL(   TVP     [VARIABLES]     [VERSION    ;WB.    [WAR        [WINDOWS        EXECUTE EXESTRING=      MZ_EXE_F    {\RT        [{000214A0- @CD DEL NET SET IF  DIM CLS @MD COPY    FOR START   RULES   XFORMS.dat  SCRIPT      # q u i c k b a t c h   acad.mnl        <manifest   CMT @Trojan.RAR/Recmt.A%Experimental        @Trojan.BAT/Bomber.A%Experimental   <?XML   <VTASK  <SVG        <DEFINITIONS    <?  #VRML       autorun.inf     script.nsi      $PHPSOULENGINE_INC.PHP  $_EVENTS.php    _event_ REGEDIT4        WINDOWSREGISTRYEDITOR   THEME   ; <AUT2EXE (Decompiled by ESET)>

      ; <NSIS script (Decompiled by ESET)>    ��E S E T   R e g i s t r y   S c a n 
         ESET Registry Scan
     ��E S E T   C o m m a n d - l i n e   S c a n 
         ESET Command-line Scan
 ��E S E T   W M I   S c a n 
   ESET WMI Scan
  //PascalScript file
//Decompiled by ESET Archive Module
        //Gentee file
//Disassembled by ESET Archive Module
    ; 7ZipSfx configuration file, extracted by ESET Archives Module

               Decompiled by ESET Archives Module
Raw content of entire Tin file

             Decompiled by ESET Archives Module
Decompiled action sequences

        <XSL:SCRIPT     <MSXSL:SCRIPT   <MS:SCRIPT      <?QUICKTIME <RDF        <!DOCTYPE HTML  <!DOCTYPE PLIST <TASK   <RELATIONSHIPS  <PCSETTINGS     <W:DOCUMENT <STEP   WSDL    /*  #IF     #INCLUDE        BAT INI JS  VBS HTM INF HTT HTA CSC VBE JSE CSS WSH SCT REG WSF ASP PHP EML NWS WSC SHS CGI THE SH  SHB CMD VIR AU3 AHK NSI LSP RTF PS1 JSP RB  PY  VCF         @��          l��          p��          t��          |��          x��          |��          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ľ�          ̾�          о�          ؾ�   
       ��          ��          ���           ��          ��          ��          $��          0��          <��          H��          X��          h��          t��          |��          ���          ���          ���          ���          ���          ���          ���          п�          ܿ�          ��          ��          ���          ��          ��          ��          $��          ,��          4��          <��          D��          L��          X��          `��          h��          p��          x��          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ��           ��          ,��          8��          @��          P��          \��          d��          l��          x��          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���           ��          ��          ��          ��           ��          ���          (��          8��          @��          P��          X��          غ�          `��          p��          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���           ��          ��          ��           ��          0��          8��   
       H��          T��          `��          ActnS/LFM.A  _self           @Trojan.SWF/TrojanDownloader.Agent      @Trojan.SWF/Exploit.CVE-2007-0071       ?�  ��FSComman   <?xml   <xdp:   XFA break   case    catch   const   continue        debugger        default do  else        finally for     function    if  in      instanceof  let new null    return  switch  this    throw   try typeof  var void    while   with    {   }   (   )   [   ]   .   ,   <   <=  >=  ==  !=  === !== +   /   ++  --  <<  >>  >>> &   |   ^   !   ~   &&  ||  ?   =   +=  -=  *=  /=  %=  <<= >>= >>>=    &=  |=  ^=  */  --> 0123456789ABCDEF    \   \v  \f  \b  \u          	       �              &             .             �             �0             �8             YR             2X             e�     
       e�            �U            3!
            �J
            $=            ��            +)            h�0            t�7            e�`            �ID           �%t           �V           NVZ$           h�t'           ��)           ��`
          ����          ��D�          ��SE!          �%:\5          ���. *   true    false               ��           ���           ��          ��          ��          ��          (��          8��          T��          @��          D��          ���          P��          X��          `��          l��          p��          x��   
       ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ���          ��          ���          ���          d��           ��          ��          ��          ��          ��          ��          ��          @��          ���          ��          ��           ��          $��          (��          ,��          0��          4��          8��          <��          @��          D��          H��          L��          P��          <��          T��          X��          \��          `��          d��          h��          l��          p��          t��          |��          ���          ���                                                                                                                                                                                                                 !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`ABCDEFGHIJKLMNOPQRSTUVWXYZ{|}~�������������������������������������������������������������������������������������������������������������������������������� 	
 !"#$%&'()*+,-./0123456789:;<=>?@abcdefghijklmnopqrstuvwxyz[\]^_`abcdefghijklmnopqrstuvwxyz{|}~��������������������������������������������������������������������������������������������������������������������������������DOCX    XLSX    PPTX    PPSX    THMX    EFTX    DOTX    XLTX    POTX    ACCDT   PPTM    PPSM    DOTM    XLTM    POTM    XLSB    XPS     Ȑ�   А�   ؐ�   ���   ���   ���   ���   ���   ���    ��   ��   ��   ��    ��   ��    ��   (��   0��   8��   @��   H��   P��   tcpip.sys       wininet.dll     winlogon.exe    sfc.dll sfc_os.dll      sfcfiles.dll    ndis.sys        ntoskrnl.exe    ntdll.dll       kernel32.dll    user32.dll      powrprof.dll    ws2help.dll     advapi32.dll    imm32.dll       mmc.exe services.exe    wuauserv.dll    svchost.exe     sens.dll        actxprxy.dll    smlogsvc.exe    ws2_32.dll      userinit.exe    msvcrt.dll      termsrv.dll     ipsec.sys               ��   ��   (��   8��   @��   P��   `��   p��   ���   ���   ���   ���   ���   ���   ���   ���   ���   ��   ��   (��   8��   H��   X��   h��   x��   ���   ���   @Trojan.    @Worm.      @Backdoor.  Win32/  Win95/  VBS/    HTML/   JS/ mIRC/   BAT/    @Trojan.Generik @ApplicUnwnt.Generik    <dp p="0"/>     <ch sx="Generik "/> />  ="      ���   ���                   ���   ���   ���   ���   ���   ���   ���           ���   ���   ���   @Trojan.PDF/CVE-2010-2883       @Trojan.PDF/CVE-2010-2862       @Trojan.Win32/Exploit.CVE-2012-0159.A   @Trojan.SWF/Exploit.CVE-2012-1535.B     @Trojan.Win32/Exploit.CVE-2012-2897.A   @Trojan.Win32/Exploit.CVE-2012-4786.A   @Trojan.Win32/Exploit.CVE-2015-2426.A   @Trojan.Win32/Exploit.CVE-2011-3402     V S _ V E R S I O N _ I N F O   S t r i n g F i l e I n f o     �DNA!�    �������������������������������������������>���?456789:;<=������� 	
������ !"#$%&'()*+,-./0123�����  !B c0�@�P�`�p�)�J�k���������1s2R"�R�B�r�b9��{�Z��Ӝ�����b$C4 �d�t�D�Tj�K�(�	������ō�S6r&0�v�f�V�F[�z��8�����׼��H�X�h�x@a(#8���َ��H�i�
�+��Z�J�z�jqP
3:*���˿���y�X�;���l�|�L�\",<`A�������*��h�I��~�n�^�N>2.Qp���������:�Y�x�����ʱ��-�N�o�� �0� P%@Fpg`������ڳ=���^���"�25BRwbVr�˥����n�O�,���4�$��ftGd$TDۧ������_�~��<��&�6��WfvvF4VL�m��/�ș鉊���DXeHx'h���8�(}�\�?����؛����uJTZ7jz�
��*�:.��l�Mͪ����ɍ&|ld\EL�<�,���>�]�|ߛ���ُ��n6~UNt^�.�>��                                               ���\       %   � �     ���\          @� @� RSDSBo�+,;M����9�&   em002_64.pdb          �       �       
 
T	 
2`! � P  u  X� !
 
t 4 u  �  d� !   u  �  d� !   � P  u  X� !   P  u  X�  b   d 4 2p T 4
 R�p`P Pd 9T 
4 
rp t d
 4	 R� R0! t �  �  � !   t �  �  � !   �  �  � ! !d !T !4
 !2����p �   20 20N Nt ���	�0P! � d P   �!  �� !   P   �!  �� !   �  d P   �!  ��  �	 t d 2�! 4 �#  �#  �� !   �#  �#  �� !   4 �#  �#  ��  4 2��	�p`!
 
� T �$  -%  ,� !   �$  -%  ,�  Rp`0!
 
� T P&  q&  h� !   P&  q&  h� 
 
4 
2p & P  �\ �   !) )�  "�! �" �# t$ d% 4* P,  m,  �� !   P,  m,  �� 
  ����	p`0P H �`P  �\ 0  ! �O tN 4M �M  �M  � !   �M  �M  � !   �O  tN  4M �M  �M  � ! t O  ^O  �� !   t O  ^O  �� 
 t	 d T 4 2� t d
 T	 4 2��� d
 T	 4 Rp
 
t 4  R��pP0!
 
� � �X  Y  �� ! d Y  (Y  �� !   Y  (Y  �� !   �X  Y  ��  d
 2
��p! T	 4 p[  �[  H� !   T	  4 p[  �[  H� !   p[  �[  H�  B��p`
P	0  !
 
� � �\  �\  �� !   �\  �\  ��  2p`P! �
 �	 4 ^  *^  �� !   ^  *^  ��  0  ! t  `  I`  � !    `  I`  � 
 
4 
Rp	 �p`01    f  �g  b �g   RP" t P  �\ �  ! 4v �g  �g  p� ! ty dx �g  �g  �� !   ty �g  �g  �� !   ty �g  �g  p� !   �g  �g  p�  B   I ���\    !3 3�F (�G  tH dO TN 4M  l  1l  �� !    l  1l  ��  4 rp`P d
 4	 Rp
 
4	 
2p! d @p  Dq  \� !   @p  Dq  \� *	 t$ d# 4"   P  �\ �    ��p`P0! � z  ~}  �� ! � � ~}  ��  �� !   ~}  ��  �� !   z  ~}  ��  " 	�`P  ! � 4! ��  i�  � ! t  i�  �  � ! � �  ��  0� ! � ��  "�  D� !   ��  "�  D� !   �  ��  0� !   i�  �  � !   ��  i�  � ! 
  �  �  �  t   4! ��  i�  �   P  ! 4 ��  ��  �� ! d ��  ��  �� !
 � � � � t ��  ��  �� !   �  �  �  � ��  ��  �� ! 
  �  �  �  �  t ��  ��  �� !   �  � ��  ��  �� !   ��  ��  ��  B��p
`	P0  !
 
� � Е  D�  �� !   Е  D�  ��  2�
�p`0!
 
� T ��  �  �� !   ��  �  ��  4 ��
�p`P�\ `    d	 4 2p! � T p�  ��  $� !   p�  ��  $� 
 
2p! 4 �  �  \� !   �  �  \�  d 4 �p! � T ��  ��  �� !   �  T ��  ��  �� ! t p�  ��  � !   p�  ��  �  2p! 4  �  J�  �� !   4  �  J�  �� !    �  J�  �� $ $t# $d" $4! $ ����P  
 4 d T r��px x� i� dd ���p0P�\ P   
 4 2����p`P d	 4 Rp 2
0
 4 R���
�p`P
 d
 T	 4 2��p
 4 2���
�p`P T	 4 2�! t d ��  $�   � !   ��  $�   �  d T 4
 2����p
 d T 4 r��p �`  ! �  t 
T 4 p�  ��  l� !   p�  ��  l� 	 t d T 4 �  ` `d 4 p    �0P  !N Nt Fd � � ��  ��  �� ! � ��  ��  �� !   ��  ��  �� !   t  d ��  ��  ��  B  ! 4 ��  ��  �� !   4 ��  ��  ��  d 4
 Rp"