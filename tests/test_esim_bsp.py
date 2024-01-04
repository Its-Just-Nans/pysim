#!/usr/bin/env python3

# (C) 2023-2024 by Harald Welte <laforge@osmocom.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import logging
import base64

from pySim.utils import b2h, h2b
from pySim.esim.bsp import *

class BSP_Test(unittest.TestCase):
    shared_secret = h2b('8902dca391bbb22570fe60c176076246f568b1941265dff1d729e63039658089')
    eid_bin = h2b('89049032123451234512345678901335')
    def test_kdf(self):
        s_enc, s_mac, icv = bsp_key_derivation(self.shared_secret, 0x88, 16, b'\x80'*8, self.eid_bin)
        self.assertEqual(s_enc, h2b('d782d575b22a38334556a3d9a1e2ae6b'))
        self.assertEqual(s_mac, h2b('a35addc192ae8f934e2932116c7e89e7'))
        self.assertEqual(icv, h2b('734bc93ddb10c71c5ad13d420dc08b5b'))

class BSP_Test_mode51(unittest.TestCase):
    """This test was created using hex-dumps from a log/trace of a 3rd party SM-DP+.  We therefore use these
    test vectors to verify our implementation is in agreement with that other implementation."""
    shared_secret = h2b('c9a993dd4879a8f7161f2085410edd4f9652f1df37be097ba96ba2ca6be528fe')
    eid_bin = h2b('89049032123451234512345678901235')

    def test_kdf(self):
        s_enc, s_mac, icv = bsp_key_derivation(self.shared_secret, 0x88, 16, b'\x80'*8, self.eid_bin)
        self.assertEqual(s_enc, h2b('472f5bfadd97f21d34f3ce9b51b92751'))
        self.assertEqual(s_mac, h2b('9ec07f5b36a13e12a991d66e294e6242'))
        self.assertEqual(icv, h2b('406d507b448a699e7a36a38494debbde'))

    def test_ciphering(self):
        bi = BspInstance(h2b('472f5bfadd97f21d34f3ce9b51b92751'), h2b('9ec07f5b36a13e12a991d66e294e6242'), h2b('406d507b448a699e7a36a38494debbde'))
        output = bi.encrypt_and_mac(0x87, h2b('bf2400'))
        self.assertEqual(output[0], h2b('8718f6fe031e4b9cfe87c8e1e62f3fde85c49412d7722a6a2d89'))

        output = bi.mac_only(0x88, h2b('bf252d5a0a98001032547698103214910947534d415f54455354921147534d415f544553545f50524f46494c45950100'))
        self.assertEqual(output[0], h2b('8838bf252d5a0a98001032547698103214910947534d415f54455354921147534d415f544553545f50524f46494c459501008a62cc9adbb5ccbc'))

        output = bi.encrypt_and_mac(0x87, h2b('bf26368010000102030405060708090a0b0c0d0e0f8110010102030405060708090a0b0c0d0e0f8210020102030405060708090a0b0c0d0e0f'))
        self.assertEqual(output[0], h2b('8748a14c800a001992351cd46ad2945654674369701d82b7b46567652bc8fbed234939fc57fba748015525fd6c651e9d3d1330652d42a0cfad950e912122af4ec5362d3c0bc535729c40'))

        # new key material after replaceSessionKeys
        bi = BspInstance(b'\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f',
                         b'\x02\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f',
                         b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f')

        segment0 = h2b('a048800102810101821a53494d616c6c69616e63652053616d706c652050726f66696c65830a89000123456789012341a506810084008b00a610060667810f010201060667810f010204b08201f8a0058000810101810667810f010201a207a105c60301020aa305a1038b010fa40c830a98001032547698103214a527a109820442210026800198831a61184f10a0000000871002ff33ff01890000010050045553494da682019ea10a8204422100258002022b831b8001019000800102a406830101950108800158a40683010a95010882010a8316800101a40683010195010880015aa40683010a95010882010f830b80015ba40683010a95010882011a830a800101900080015a970082011b8316800103a406830101950108800158a40683010a95010882010f8316800111a40683010195010880014aa40683010a95010882010f8321800103a406830101950108800158a40683010a950108840132a4068301019501088201048321800101a406830101950108800102a406830181950108800158a40683010a950108820104831b800101900080011aa406830101950108800140a40683010a95010882010a8310800101900080015aa40683010a95010882011583158001019000800118a40683010a95010880014297008201108310800101a40683010195010880015a97008201158316800113a406830101950108800148a40683010a95010882010f830b80015ea40683010a95010882011a83258001019000800102a010a406830101950108a406830102950108800158a40683010a950108a33fa0058000810102a13630118001018108303030303030303082020099300d800102810831323334353637383012800200818108313233343536373882020088a241a0058000810103a138a0363010800101810831323334ffffffff8201013010800102810830303030ffffffff820102301080010a810835363738ffffffff830101a182029ea0058000810104a18202933082028f62228202782183027ff18410a0000000871002ff33ff0189000001008b010ac60301810a62118202412183026f078b01028001098801388109082943019134876765621482044221002583026f068b010a8801b8c7022f06621a8202412183026f088b0105800121880140a507c00180c10207ff621a8202412183026f098b0105800121880148a507c00180c10207ff62168202412183026f318b0102800101880190a503c1010a62118202412183026f388b010280010e880120810d0a2e178ce73204000000000000621982044221001a83026f3b8b0108800202088800a504c10200ff62198204422100b083026f3c8b0105800206e08800a504c10200ff621282044221002683026f428b0105800126')
        output = bi.encrypt_and_mac_one(0x86, segment0)
        self.assertEqual(output, h2b('868203f80fd36b066b43e53906b33263c4141d18036fcac7bde47faed79e76514d39f1f405d9785ff04badf379a96bcf4685eb861239da34eeb213d0cd1e0d85e96e36097a52f600907e08b6f01232eb3792a00cc6b3288cc832c7f30357edfe0818d1f39ad8d55b5bd5d9c65917d0d16ee7e1421a44453714d66209bf441425bf6d153a85ba7e7406d58a4c46fb930bb14eefd6a853434619805429cbbb003bd5a56e7bceaf4666eb352ad46f47ea572c6ad311683803db3bec4d783583858f2ecfbaec3ed780fb3e3a645b1bf5cfd1047e5862c4a8877382dabd6aef6fa72ec6378ce7b21502d3267514b29bd589703ee7bd5b1e6d868b6b7c55006bc32406a924f44bfdb6c801d490450a54633bbd66bb0ece8b3a9be09433c537f3e3b2b8e45833365a94479b1895e9ba13387fca116565c267b6bc1274c82510b21ac9fa77574412351468fd1eac8928c9494e5eb8a909d9372476c62e8a2b556b557a79cdb47503ba5d9fd86d1962c23b3289f37df9a05668957df34c37806359af1d8dfecedf9bbf4888be9753f2b449ce4e5cde510572f9be4fb506f329a848c4583ac9ac710e53d512ad504f2e3769c2911c34f84ad0622c5428446d1e9c59bb6b2029f231b05ef45d3ec60fceff121ba684a023037b753f855e1067b8ad02783c04eb81ba47fcec0947bbc9661d90c6f00c0f4e6f9c22e0b25905379f8b265b436a4a74253a64c5734f956d134cf5b6c0671125b20b735f405fee1fc1941ed141734fa6856e898dc655fb91b045b3797d14b97a68ed3480ec137565d6c4d007f95ee705d452d0344ce9e9bbd0712f399ef8604f3f472b403ea64f00c969fd30a012cb8be049c54556994117fc5f6043930107774910be5f47c780427de063a56d45400a814c86dfcc2465262baf273a6ca89e77bb8c73efe2d22d975516b80c648404b10d3f329776a21251bedf445ade24b656e8635f0d7fe39772d942d9432766efb5152c6e990123c52744f1c402962a381ff2aaddaa1bd522a9b65a229f9adcd4099475b3f9ba45161ee35206365181e1d69d263d8d27444a7c3a2d7ddbb398ac5affea28cb0373057dad7741e52adb95822fee5157ce3c0ad978c5231a219ca0726d50eeb0c69d579094a54820194aeef13a365d85c52257f51cb65c567e0cdf1ce38b80eaa4d131ab7086e303c5728cf41a25df954d60ac12400d2a2990e67dbeff866736937beb8fce526be1dd5dc5d77d00b8783b34691a3e9bda7e697eec4cfa70b25914795af23ec6d258530f71402b9230947dc99f9140b16a54ba1291f54ef736de6711c1ae074b627dfc2fc5d5250f812b7ecd1d0f5020a3acf20ad5759cd9e761ce21882977f7db66aaba2d8f5190f6f23996af14b670ccac066c93af06a41f19d9ee712ce13fbe73b99e55401b208b991c8ced12d34c'))

        segment1 = h2b('880062158202412183026f438b01058001028800a503c0018062128202412183026f468b036f060a8001118800810c0253494d616c6c69616e636562118202412183026f568b0108800101880128810100621b8202412183026f5b8b0105800106880178a508c00180c203f0000062168202412183026f5c8b0102800103880180a503c0018062168202412183026f738b010580010e880160a503c00180020107810700f1100000ff0162118202412183026f788b01028001028801308102004062118202412183026f7b8b010580010c88016862168202412183026f7e8b010580010b880158a503c0018002010781040000ff0162168202412183026fad8b010a800104880118a503c10100020103810102621382044221000483026fb78b010a800104880108810419f1ff0162158202412183026fc48b01058001808800a503c0018062168202412183026fe38b01058001128801f0a503c0018002010f810300000162168202412183026fe48b01058001508801c0a503c00180a225a0058000810105a11ca01a301880020081810831323334ffffffff82020081830101840122a43aa0058000810106a131a12f8001018101018210000102030405060708090a0b0c0d0e0f83100102030405060708090a0b0c0d0e0f008603010203a681bba0058000810107a1444f07a00000015153504f08a0000001515350414f08a000000151000000820382dc0083010fc90a810280008201f08701f0ea11800f0100000100000002011203b2010000a26c3022950138820101830101301730158001808610112233445566778899aabbccddeeff103022950134820102830101301730158001808610112233445566778899aabbccddeeff1030229501c8820103830101301730158001808610112233445566778899aabbccddeeff10a681c0a0058000810108a1494f07a00000015153504f08a0000001515350414f10a00000055910100102736456616c7565820380800083010fc907810280008201f0ea11800f01000001000000020112036c756500a26c30229501388201018301013017301580018086108811223344556677881122334455667730229501348201028301013017301580018086108811223344556677881122334455667730229501c882010383010130173015800180861088112233445566778811223344556677a8820263a0058000810109a18202184f08a000000559101001c482020a01002edecaffed020204000108a0000005591010011b636f6d2f67736d612f65756963632f746573742f6170706c657431020021002e0021000f003b002a00210066000a000e0000008a040f00000000000004010004003b04030107a0000000620101000110a0000000090005ffffffff')
        output = bi.encrypt_and_mac_one(0x86, segment1)
        self.assertEqual(output, h2b('868203f8648e034ae0dc4ce022ee1e60b130dda95e13b21b0da3de7677677f47900c1beb3637b8aa35f3a9e096c0285ffe3e931983df900b36b7e6bc4b9af14b0ee3d49637eb2d4cff314b5d00789a751dfd9554651fb2b7c66ad4e22a794d5b88cb71ccf4c05d53abeba8bd3b0c8209346f014cbdee62be4878e3fea09a96007135a6c584aa843c48972842bdbece1c439723021b3f0d535d557995beedbd2b56f416148df90cb1a4d2fa26288801d56a2cbb0a404f2fd9a73042d7a3486bfb7256c1d274aae5b7ec24e8eba28b7dce69edc44189b24186b98397b4a74831f8ab46e8e46a2ed3077d4924f5d3f6e4c1de5ddffd194e7f0f97d94ea2801d1364835c9871bae6539e3e1355c5970711d845864f04d9c1dccac0d4068dcf4664e9976509fe43fec6beb3ddc96839aba6d89bb1593c5b6ebbc32fff39c4a5bb3e5c9df6a1abc05818dbd5149733381e69521066e1bbd648eb19b00602767e90beaeb3b3b92679940a603c0500e37892d7b4fa44355c3deec8af207f89d04f83cd88603e9cb9c96f74643816e87af85a8a9d0283cdf535d1fbaefb930fd4a0dba2ae30ee9d2d9e2a31827a012a6380af42ac87f3bfd7079ddd8fa27d2299fb4d5879e9a17a5062e13cab4f7bed22ed54932fa53d630bca8592f957a7ed148e9d4f28075c2565a550694b876091a1181ba512e70fde4f28ae6968a18d721396c0fee9cd7744dee90bf85f5adddb3417b3ede9ea3cfd5eae2d820b17600ce3b95f6df38a5bc39302c5155c3f241ddfc7cee527af7f6a67868a577c39e76e26c4ed5d6aca031a97c280da27ae8de20e57a1dbab40a31e96e054f9a6f50578fd00156e37b70eead71af3258075c1ba84282aea462553504a868443b301ed99dcd5f414b720ef67cf5c4d16f1f7b9df741c2343246dcb717f3fa62b633539bdcc0082d161499caad8d097be78133dafd19777559f77c6d7a8f61323ff660613aa47cee26a4f7515204eee3c7eaa00eb55529b0ddae3436ec679fc591fe2063de94db00b5d0f041beeb80a91f108f7cf4b3b1344b0fbb437630ee437b4c7744c54009a59a9099681f3a3fa386f294c0eb4562581202a369772833efdc6e840695352de3864671e7fb0fd081ec162a2a62ea5b8a9da837f3920b4196fbe2ec912ade440537ae4a07dfc115c9c030539f278e0801bda4f15298ba50e329b18992af8b899686ec97175509d4a217d2eba8feef5f5732fc7be86370f7723896b784bd45517af86a7521e952b6be924d91a5190e3c2c65ce8924df43ddb25c529dde324a722a156df459f4b38bb062975fad9fadd27f6425e422b1abd9a7259f0bd712a486e1aa25ca848cf65c5fb888bf61ae136b68cf55cb643c198537cd83df0dbb842c5f4982ca3088cc2d8e867c3049a84b515ec39b0b774a8482099327006acff'))


if __name__ == "__main__":
    unittest.main()
