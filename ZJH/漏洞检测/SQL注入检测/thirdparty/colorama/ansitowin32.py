# Copyright Jonathan Hartley 2013. BSD 3-Clause license, see LICENSE file.
import re
import sys
import os

from .ansi import AnsiFore, AnsiBack, AnsiStyle, Style
from .winterm import WinTerm, WinColor, WinStyle
from .win32 import windll, winapi_test


winterm = None
if windll is not None:
    winterm = WinTerm()


def is_stream_closed(stream):
    return not hasattr(stream, 'closed') or stream.closed


def is_a_tty(stream):
    return hasattr(stream, 'isatty') and stream.isatty()


class StreamWrapper(object):
    '''
    Wraps a stream (such as stdout), acting as a transparent proxy for all
    attribute access apart from method 'write()', which is delegated to our
    Converter instance.
    '''
    def __init__(self, wrapped, converter):
        # double-underscore everything to prevent clashes with names of
        # attributes on the wrapped stream object.
        self.__wrapped = wrapped
        self.__convertor = converter

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def write(self, text):
        self.__convertor.write(text)


class AnsiToWin32(object):
    '''
    Implements a 'write()' method which, on Windows, will strip ANSI character
    sequences from the text, and if outputting to a tty, will convert them into
    win32 function calls.
    '''
    ANSI_CSI_RE = re.compile('\001?\033\[((?:\d|;)*)([a-zA-Z])\002?')     # Control Sequence Introducer
    ANSI_OSC_RE = re.compile('\001?\033\]((?:.|;)*?)(\x07)\002?')         # Operating System Command

    def __init__(self, wrapped, convert=None, strip=None, autoreset=False):
        # The wrapped stream (normally sys.stdout or sys.stderr)
        self.wrapped = wrapped

        # should we reset colors to defaults after every .write()
        self.autoreset = autoreset

        # create the proxy wrapping our output stream
        self.stream = StreamWrapper(wrapped, self)

        on_windows = os.name == 'nt'
        # We test if the WinAPI works, because even if we are on Windows
        # we may be using a terminal that doesn't support the WinAPI
        # (e.g. Cygwin Terminal). In this case it's up to the terminal
        # to support the ANSI codes.
        conversion_supported = on_windows and winapi_test()

        # should we strip ANSI sequences from our output?
        if strip is None:
            strip = conversion_supported or (not is_stream_closed(wrapped) and not is_a_tty(wrapped))
        self.strip = strip

        # should we should convert ANSI sequences into win32 calls?
        if convert is None:
            convert = conversion_supported and not is_stream_closed(wrapped) and is_a_tty(wrapped)
        self.convert = convert

        # dict of ansi codes to win32 functions and parameters
        self.win32_calls = self.get_win32_calls()

        # are we wrapping stderr?
        self.on_stderr = self.wrapped is sys.stderr

    def should_wrap(self):
        '''
        True if this class is actually needed. If false, then the output
        stream will not be affected, nor will win32 calls be issued, so
        wrapping stdout is not actually required. This will generally be
        False on non-Windows platforms, unless optional functionality like
        autoreset has been requested using kwargs to init()
        '''
        return self.convert or self.strip or self.autoreset

    def get_win32_calls(self):
        if self.convert and winterm:
            return {
                AnsiStyle.RESET_ALL: (winterm.reset_all, ),
                AnsiStyle.BRIGHT: (winterm.style, WinStyle.BRIGHT),
                AnsiStyle.DIM: (winterm.style, WinStyle.NORMAL),
                AnsiStyle.NORMAL: (winterm.style, WinStyle.NORMAL),
                AnsiFore.BLACK: (winterm.fore, WinColor.BLACK),
                AnsiFore.RED: (winterm.fore, WinColor.RED),
                AnsiFore.GREEN: (winterm.fore, WinColor.GREEN),
                AnsiFore.YELLOW: (winterm.fore, WinColor.YELLOW),
                AnsiFore.BLUE: (winterm.fore, WinColor.BLUE),
                AnsiFore.MAGENTA: (winterm.fore, WinColor.MAGENTA),
   ��(  ���ܿg� �]Z$  ��� 8�� �d�.  ��]�\�� �(�:  ���� �� Џ�E  ��((��� �i�Q  �� Q$� �(]  ������� й|i  ���g�� Нos  ��'�6T� �  ���<nt� Ш�  ��p	��� �p�  ��tE��� �nƣ  ��'l�Y� �>��  ��]d�|� �3׺  ���Q �� Й{�  ��zEa�� �3H�  ��ўL=� �E%�  ��J�x0� ����  ������� �m��  ��p��
� Ѕ��  ���|� �8�  ����� �J�  ����H�� ���  ��Ï��� �/�  ��F���� Р��  ��q+�  Я�  ����� ��  �� r! �ռ  hj�&���0���* R�z�� ňD44  ����/�� �si<  ��E� �J�o  ���sw� В�H  ����^> �f�T  ������ Рo^  �����.� ��j  ��ޜX� Ћat  ���0�� ��z~  ���?zk� �:{�  ���4A[� иӖ  ��0; x� ��9�  ��ܷw�� �B%� `��"�����Ćغ  ��a��� д��  H ��r(� Э�� ���+� �/R�  ���O��� �/��  ����� ����  ��N
��� �Y9�  ���	��� �J�   ���U�� �i  ���D�L� �F�  ��Ļo� �s�"  ����8�� �:�.  ��üy��`�:�:  ������� ЦuF  ��<&� �PHR  ����A�� ��^  ����.� �:�j q����  �߬v  ���nԧ� ��  ��ܟ�� С��  ����b� ��E�  ��D��� �qm�  ���"�� �RK�  ������ Ї!�  ��5��� ���  ���|� P�$�  ��B��w� ����  ��7@;#� �?[� �'��C�������  hTD�5� �P?�  �����  Ш��  ��+��� �>��  ����P� �"��  ���{� ����  � ��t�� ���  ���ݒ�� �q  ����� �a  ��5�	 л,  ����|� Н�  �����U� �1*  ��n�S� ШY6  ���G�� �r�B  ��a/�s� �ҍN  ���:��� ��Z  ���E�� ���f  ��Ń��� О�r  ��lِ3� КW~  ��t��2� ��  ��,v4� �R�  ���H� �|�  ��_	0�� У��  ���L�\� �Ӻ  ����w� �TZ�  ��쨪� �f��  ��mC~� �G>�  ��q%�� � ��  ��ςDy� З��  ���
�6� ��  ����y"� У�  ���<3;� ІC  ��'M�� �׃"  ���x��� �dP,  ���V� ��6  ��"��� ��RB  ����� �qhN  ��w�;:� �$�Z  ��K82�� �1f  ����� ���r  ������� �+~  ��s���� �9��  ����L%� ����  ���G^� �"��  ��+ƌ�� ДQ�  ��S�+�� ���  ����ɵ� �KG�  ����Շ� �^�  �����E� ���  ������� Э��  ��ҍ_
� �(��  ���}d�� �ʅ�  ��hO� ��D�  ����a� Р�
  ������� ���  ���1�� О8   ���ذ�� �0+  ���P�� �W�7  ����� �i�C  ���U=s� ���O  �4 �� ��[  ���x������c  ���E,�� �K}n  ���{�� ��z  ���9�� ����  ��ԓf[  �En�  ��%���� Ќ��  ��R6ֻ� �� �7�L�Ԁ� Ѓ��  ��p�$3� ��K�  ���J,� Pn�  ���K�� Эw�  �� Q� Еz�  ���/�m� �}��  ��9%k� ��N�  ����M�� �� �'�rÅ����  ����E�� �ڟ�  ��ɠRQ  Д�  ��� �� Х"(  ��w�Q�� ��W4  ���O�� �W@  ��>&��� ЫL  ��5%��� ж�X  ��,c�� �!�d  ��� �W  �r�p  �����[� ���|  ��VsV ��1g�  ���Q��� ��ؔ ے�� Ы�� 
Sp3�� Е$� V� oh�� �gѠ :T ���E� ��x� ��R�������  ����*�� �V��  ���wX��@�8��  ��d�:� �h��  ���lW�� оf�  ��p� �У�  ��vJ.�� �O��  ���T~�� ��R�  ��N�2� ��?�  ���CA�� И�  ��eǤ�� ��-	  ���R� � ��  ���{>�  А�!  ��jD������-  ��\e� �z�9  ���iW� ЉE  ����d�� �1Q  ���w��� З�]  �����Q� ��<i  ��12��  Ь_u  ��<�T� ��4�  ����t� �ˍ  �����F� �Ԏ�  ���e��  С-�  ������ �ګ�  ��Ln��  �ݽ  ������ �*�  ��a1 �|E�  ��ÉY�� ����  ���;��� �nR�  ���
�� ���  ��5�cy� ��  ��>Q˧� �]�  ��L� �� Р;  ���mY� ��)  ��U6't  г�5  ���_��� �e�A  ��k��S �+&M  ���� ��Y  ��n�j�� СKd  ��ۺ�� АUo  ���ӈ�� ��z  ��~>S�� �ڼ�  ���Hs�� �܈�  ��Ϗ�����h{�  ��|vuZ� ���  ��)�m�� Ј�  ��Ҭ׿  �C �  ����qT  Ё��  ���-)k� ����  ���m� Ы��  ��²�5� ���  ��<n��� В��  ���ސ�� �t	  ���hk�� ���	  ��'�� �)  ���h9� Ѐ�   ���6��� �c�,  ���?)�� �1y8  ����E� ��D  ��kF�c� �9�P  ��]�E� ��\  ���8r�� ��dg  ���W� ���r  ���(��� �>W~  ���&��� ��  ��$t�� �4
�  ��]��a� �H��  ��.��� ���  ��"�� �˖�  ������ ��  ��.�+�� �\Q�  ��<�&�� ����  ��~p �� �@��  ������ Г��  �����5� ��  ��-�ab� У  ���Z/� ���  �����:� Ѐ�  ���w�U� М�  ��+T��� ��M  ���V��� ��$  ��5 ��� ��@.  ������ ��+:  ��Ⱥ�^� ��RF  ���/}�� ��R  ��$���� �P^  ��ι6w� Ж�j  ���T�� Чv  ���T�� Чv  ����� ��1�  ���P� �w� �R �	���@��=�  ����� �X٘  ��!.��� �e}�  ���� Ы��  ��UA� ���� ���$�>�� Ъ6�  �����k� �t��  ����#�� ��?�  ���Hк� ��¬  ���D��� ��h�  ��!Ȫ� �}^�  ��J��� ТD�  ��P/0� ���  ����b� �>�  ������ Шv�  ���lM�  ����  ���U5�� �ӝ�  �����P� �|�  ��(/� к,  ����$a �&j  ��^���� �*  ��5q��� �Cm2  ��6��� �1�>  ���49|� � eJ  ��8V��� ��V  ��, +� Ћjb  ���s�  Ч�n  �� s�� ЇYz  �����&� �.l�  ���l�{� �%-�  ��N.�� ���  ���e��� ��q�  ��!�A�� �kݵ  ���Xx� �z��  ��z��#� ���  ������ ���  ����3� ЮH�  ��e>�Z ���  ��ԋ�|� Џz�  �����  �l�   ��R��$� �G,   ���	H"� �U   ���#A�� ���)   ���כ7� �P5   ��U� >� ЬA   ���׻� �
�M   ����Q  ��yY   ����U
 и�e   ��9�S�� Љ�q   ��2��� �$}   ��Vl�C� Ф��   ���e��� �yg�   ���X�� в5�   ���O�
� �٘�   ����R� �vq�   ��i��� �ǋ�   ��c9٭� �G��   ����� ��;�   ���_��� �d��   ��ۜ �Ͱ��   ��لk�� �W��   ��d��u� �:�!  ��aE*�  �, !  ���J��  ��#!  ��^^�� Ѝ/!  ��E�ͤ� ��;!  ($%��� �j�G!  ��to�o� А�G!  ��p"� �LO!  ��7��e� ��yZ!  ����b> r���e!  ��i�#�� �ȉq!  ��IM�� ��@}!  ��� 0� �]��!  ���ە�� П��!  ��H]�O� ��o�!  ���g�� �E�!  ���[�  ���!  ��	���� �㫪!  ����  ���!  ��w��<� �Թ�!  ��gL��� ���!  ��f'a�� �j��!  ������ Џ��!  ����(� �r{�!  �����	� ��P�!  ���G�&� �b�!  ��g�f� М�
"  ��)�S� �AE"  ��T5��� �^"""  ��gx�� �Z."  ��xb� �`�:"  ���7�� ��sD"  ��S+��� ��P"  ����� �`#\"  ������� �h"  ��k���� �4wt"  ����b�� �~!�"  ���y��� йӌ"  ��L �� L�"  ����-h� �5��"  ������� ���"  ��|0A]� ����"  ���5��� Ф%�"  ���g�w� І<�"  ���p�1� ��
�" �����  �GE�"  ������� �F��" ~�KT� Љ �"  ��j'��� ��#  ��U.z� �/	# �����/� ���# 0�eD$������#  ��*/�� ��%#  ���Q�� ��1#  ��CΟ�� Е�=#  ���L� иKI#  ��'7�� ���U#  ����<�� �]ia#  Hb� G� �#�m#  ���Z{f� ��'y#  ������ �S��#  ��M�[� �mՑ#  ����v�� ��s�#  ������ �B�#  ���xgZ� лֵ#  ���-��  В��#  ��ǚ�� �O�#  ����B�� Ј��#  ��鳫�� �y��#  ���3��� �	]� ����   ��l�# ���>�  е��#  ���M�� �=<$  �����>� �ޛ$  ����*�� ���$  ��ӳ}� �ý'$  ������� �~3$  ������ �e�?$  ���S�R �"xK$  ����N�  �*�W$  ��"�� І�c$  ���?�� �So$  ��`�O�� ж{$ ����U бr�$  ���3h�� Зԑ$  