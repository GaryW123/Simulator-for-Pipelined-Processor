#/* On my honor, I have neither given nor received unauthorized aid on this assignment */
import sys
import os
import math
import random
import numpy as np
import string
file_handle = open('sample_simulation.txt', mode='w')
file_dissembly= open('sample_disassembly.txt', mode='w')
#Register R00~R24
Cycle=0
Reg=np.zeros(32,int)
Imm=[]
ImmAddr=[]
DataAddr=0 #记录数据区开头地址
Data=None #Data
PC=256#PC
InsCat1=['J','JR','BEQ','BLTZ','BGTZ','BREAK','SW','LW','SLL','SRL','SRA','NOP']
InsCat2=['ADD','SUB','MUL','AND','OR','XOR','NOR','SLT','ADDI','ANDI','ORI','XORI']
def printReg():
#    print("Registers")
    file_handle.write("\nRegisters\n")
    for i in range(len(Reg)):
        if i==0:
      #      print("R00:\t{}".format(Reg[i]),end='')
            file_handle.write("R00:\t{}".format(Reg[i]))
        elif i==8:
        #    print("\nR08:\t{}".format(Reg[i]),end='')
            file_handle.write("\nR08:\t{}".format(Reg[i]))
        elif i==16:
         #   print("\nR16:\t{}".format(Reg[i]),end='')
            file_handle.write("\nR16:\t{}".format(Reg[i]))
        elif i==24:
        #    print("\nR24:\t{}".format(Reg[i]),end='')
            file_handle.write("\nR24:\t{}".format(Reg[i]))
        else:
        #    print("\t{}".format(Reg[i]),end='')
            file_handle.write("\t{}".format(Reg[i]))
 #   print('\n')
    file_handle.write('\n')
    return
def printData():
 #   print("\nData",end='')
    file_handle.write("\nData")
    for i in range(len(Imm)):
        if (ImmAddr[i]-DataAddr)%32==0:#8个为1组
   #         print("\n{}:\t{}".format(ImmAddr[i],Imm[i]),end='')
            file_handle.write("\n{}:\t{}".format(ImmAddr[i],Imm[i]))
        else:
     #       print("\t{}".format(Imm[i]),end='')
            file_handle.write("\t{}".format(Imm[i]))
#    print('\n')
    file_handle.write('\n\n')

#补码str转原码str
def com2ori(ori_str: str):
    # 如果符号位为正，则原码与补码相同
    if ori_str[0] == '0':
        return ori_str
    elif ori_str[0] == '1':#负数 取反加一
        value_str = ""
        # 数值位按位取反
        for i in range(len(ori_str)):
            value_str+='1' if ori_str[i] == '0' else '0'
        # 数值位加 1
        n = int(value_str, 2) + 1
        com_str = bin(n)[2:]
        if len(com_str) >= len(ori_str):
            # 说明进位到符号位了
            com_str = '0' + com_str[1:]
        else:
            # 0不够，中间填充0
            n = len(ori_str) - len(com_str) - 1
            for i in range(n):
                com_str = '0' + com_str
            com_str = '1' + com_str
        return com_str

#原码str转十进制int
def ori2dec(bin_str: str):
    # 如果为正数
    if bin_str[0] == '0':
        return int(bin_str, 2)
    elif bin_str[0] == '1':
        return -int(bin_str[1:], 2)
#补码str转十进制int
def com2dec(com_str: str):
    ori_str = com2ori(com_str)
    return ori2dec(ori_str)
#十进制转二进制原码
def dec2ori(dec_num):
    bin_tmp=bin(dec_num)
    if bin_tmp[0] == '-':  # 为负数 符号位置1
        bin_tmp = '1' + bin_tmp[3:]
    else:  # 为正数 符号位置0
        bin_tmp = '0' + bin_tmp[2:]
    return bin_tmp
#位数补齐32位(保留符号）
def converTo32bit(bin_str:str):
    if len(bin_str)<32:
        bin_str=bin_str[0]+(32-len(bin_str))*'0'+bin_str[1:]#补齐
    return bin_str


#逻辑左移
def SLL(dec_num,b):
    bin_num=0
    if dec_num==-4294967296:
        bin_num="10000000000000000000000000000000"
    else:
        bin_num=dec2ori(dec_num)
        bin_num = converTo32bit(bin_num)
        bin_num=com2ori(bin_num)
    tmp=bin_num+b*'0'
    bin_num=tmp[b:]

    return ori2dec(bin_num)

#逻辑右移
def SRL(dec_num,b):
    if dec_num==-4294967296:
        bin_num="10000000000000000000000000000000"
    else:
        bin_num = bin(dec_num)
        if bin_num[0] == '-':
            bin_num = '1' + bin_num[3:]
        else:
            bin_num = bin_num[2:]
        bin_num = converTo32bit(bin_num)
        bin_num=com2ori(bin_num)
    tmp=b*'0'+bin_num
    bin_num=tmp[0:32]
    return ori2dec(bin_num)
#算数右移
def SRA(dec_num,b):
    if dec_num==-2147483648:
        bin_num="10000000000000000000000000000000"
    else:
        bin_num = bin(dec_num)
        if bin_num[0] == '-':
            bin_num = '1' + bin_num[3:]
        else:
            bin_num = bin_num[2:]
        bin_num = converTo32bit(bin_num)
        bin_num=com2ori(bin_num)
    sign=bin_num[0]
    tmp=b*'0'+bin_num
    bin_num=sign+tmp[1:32]
    return ori2dec(bin_num)

#反汇编J
def disassemble_J(instr,instr_Addr):
    instr_index = instr[6:] #取后26位
    instr_index += '00' #左移两位
    PC_up4 = bin(0x0F0000000 & instr_Addr)
    PC_up4 = PC_up4[2:6]#取PC前四位
    if len(PC_up4) < 4:#补齐
        cont = 4 - len(PC_up4)
        PC_up4 = cont * '0' + PC_up4
    instr_Addr = PC_up4 + instr_index#合成32位地址
    instr_Addr=int(instr_Addr,2)
    disassemble_ins='J'+' '+'#'+str(instr_Addr)
    return disassemble_ins
#反汇编JR
def disassemble_JR(instr):
    rs_id=int(instr[6:11],2)
    disassemble_ins='JR'+' '+'R'+str(Reg[rs_id])
    return  disassemble_ins
#BEQ 比较两个寄存器的值是否相等，相等则跳转
def disassemble_BEQ(instr):
    rs_id=int(instr[6:11],2)
    rt_id=int(instr[11:16],2)
    offset = instr[16:32]
    offset+='00'
    offset=int(offset,2)
    disassemble_ins='BEQ'+' '+'R'+str(rs_id)+', R'+str(rt_id)+', #'+str(offset)
    return disassemble_ins
def disassemble_BLTZ(instr):
    rs_id = int(instr[6:11], 2)
    offset = int(instr[16:32]+"00", 2)
    disassemble_ins = 'BLTZ' + ' ' + 'R' + str(rs_id) + ', ' + '#' + str(offset)
    return disassemble_ins

def disassemble_BGTZ(instr):
    rs_id = int(instr[6:11], 2)
    offset=int(instr[16:32]+'00',2)
    disassemble_ins = 'BGTZ' + ' ' + 'R' + str(rs_id) + ', ' + '#' + str(offset)
    return disassemble_ins
def disassemble_BREAK(instr):
    return "BREAK"
def disassemble_SW(instr):
    base_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    offset = int(instr[16:32], 2)
    disassemble_ins = 'SW' + ' ' + 'R' + str(rt_id) + ', ' + str(offset) + '(R' + str(base_id)+')'
    return disassemble_ins
def disassemble_LW(instr):
    base_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    offset = int(instr[16:32], 2)
    disassemble_ins = 'LW' + ' ' + 'R' + str(rt_id) + ', ' + str(offset) + '(R' + str(base_id) + ')'
    return disassemble_ins
def disassemble_SLL(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    disassemble_ins = 'SLL' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', '+'#'+str(sa)
    return disassemble_ins
def disassemble_SRL(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    disassemble_ins = 'SRL' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', ' + '#' + str(sa)
    return disassemble_ins
def disassemble_SRA(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    disassemble_ins = 'SRA' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', ' + '#' + str(sa)
    return disassemble_ins
def disassemble_NOP(instr):
    return 'NOP'

def disassemble_ADD(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins='ADD'+' R'+str(rd_id)+', R'+str(rs_id)+', R'+str(rt_id)
    return disassemble_ins
def disassemble_SUB(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'SUB' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_MUL(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'MUL' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_AND(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id=int(instr[16:21],2)
    disassemble_ins='AND'+' R'+str(rd_id)+', R'+str(rs_id)+', R'+str(rt_id)
    return disassemble_ins
def disassemble_OR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'OR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_XOR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'XOR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_NOR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'NOR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_SLT(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    disassemble_ins = 'SLT' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def disassemble_ADDI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = instr[16:32]
    tmp_imm=converTo32bit(tmp_imm)#转为32位
    tmp_imm=ori2dec(tmp_imm)#转为10进制
    disassemble_ins = 'ADDI' +  ' R' + str(rt_id) + ', R' + str(rs_id)+ ', #'+str(tmp_imm)
    return disassemble_ins
def disassemble_ANDI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = int(16*'0'+instr[16:32],2)
    disassemble_ins = 'ANDI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins
def disassemble_ORI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = int(16 * '0' + instr[16:32],2)
    disassemble_ins = 'ORI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins
def disassemble_XORI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = int(16 * '0' + instr[16:32],2)
    disassemble_ins = 'XORI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins




#反汇编J
def act_J(instr):
    global PC
    instr_index = instr[6:] #取后26位
    instr_index += '00' #左移两位
    PC_up4 = bin(0x0F0000000 & PC)
    PC_up4 = PC_up4[2:6]#取PC前四位
    if len(PC_up4) < 4:#补齐
        cont = 4 - len(PC_up4)
        PC_up4 = cont * '0' + PC_up4
    PC = PC_up4 + instr_index#合成32位地址
    PC=int(PC,2)-4
    disassemble_ins='J'+' '+'#'+str(PC+4)
    return disassemble_ins
#反汇编JR
def act_JR(instr):
    global PC
    rs_id=int(instr[6:11],2)
    PC=Reg[rs_id]
    disassemble_ins='JR'+' '+'R'+str(PC)
    PC-=4
    return  disassemble_ins
#BEQ 比较两个寄存器的值是否相等，相等则跳转
def act_BEQ(instr):
    global PC
    rs_id=int(instr[6:11],2)
    rt_id=int(instr[11:16],2)
    offset = instr[16:32]
    offset+='00'
    offset=int(offset,2)
    if Reg[rs_id]==Reg[rt_id]:#如果相等
        PC+=offset
    disassemble_ins='BEQ'+' '+'R'+str(rs_id)+', R'+str(rt_id)+', #'+str(offset)
    return disassemble_ins
def act_BLTZ(instr):
    global PC
    rs_id = int(instr[6:11], 2)
    offset = int(instr[16:32]+"00",2)
    if Reg[rs_id]<0:  # 如果小于0
        PC += offset
    disassemble_ins = 'BLTZ' + ' ' + 'R' + str(rs_id) + ', ' + '#' + str(offset)
    return disassemble_ins

def act_BGTZ(instr):
    global PC
    rs_id = int(instr[6:11], 2)
    offset=int(instr[16:32]+'00',2)

    if Reg[rs_id] > 0:  # 如果小于0
        PC += offset
    disassemble_ins = 'BGTZ' + ' ' + 'R' + str(rs_id) + ', ' + '#' + str(offset)
    return disassemble_ins
def act_BREAK(instr):
    return "BREAK"
def act_SW(instr):
    base_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    offset = int(instr[16:32], 2)
    memoryAddr=Reg[base_id]+offset
    Imm_id=int((memoryAddr-DataAddr)/4)
    Imm[Imm_id]=Reg[rt_id]
    disassemble_ins = 'SW' + ' ' + 'R' + str(rt_id) + ', ' + str(offset) + '(R' + str(base_id)+')'
    return disassemble_ins
def act_LW(instr):
    base_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    offset = int(instr[16:32], 2)
    memoryAddr = Reg[base_id] + offset
    Imm_id = int((memoryAddr - DataAddr) / 4)
 #   print("Imm_id=",Imm_id)
    Reg[rt_id]=Imm[Imm_id]
    disassemble_ins = 'LW' + ' ' + 'R' + str(rt_id) + ', ' + str(offset) + '(R' + str(base_id) + ')'
    return disassemble_ins
def act_SLL(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    tmp=Reg[rt_id]
    Reg[rd_id]=SLL(tmp,sa)
    disassemble_ins = 'SLL' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', '+'#'+str(sa)
    return disassemble_ins
def act_SRL(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    tmp = Reg[rt_id]
    Reg[rd_id] = SRL(tmp, sa)
    disassemble_ins = 'SRL' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', ' + '#' + str(sa)
    return disassemble_ins
def act_SRA(instr):
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    sa = int(instr[21:26], 2)
    tmp = Reg[rt_id]
    Reg[rd_id] = SRA(tmp, sa)
    disassemble_ins = 'SRA' + ' ' + 'R' + str(rd_id) + ', ' + 'R' + str(rt_id) + ', ' + '#' + str(sa)
    return disassemble_ins
def act_NOP(instr):
    return 'NOP'

def act_ADD(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    tmp= Reg[rs_id]+Reg[rt_id]
    disassemble_ins='ADD'+' R'+str(rd_id)+', R'+str(rs_id)+', R'+str(rt_id)
    if (tmp>pow(2,31)-1)or(tmp<-pow(2,31)):
        return disassemble_ins
    else:
        Reg[rd_id]=tmp
    return disassemble_ins
def act_SUB(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    tmp = Reg[rs_id] - Reg[rt_id]
    disassemble_ins = 'SUB' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    if (tmp > pow(2, 31) - 1) or(tmp < -pow(2, 31)):
        return disassemble_ins
    else:
        Reg[rd_id] = tmp
    return disassemble_ins
def act_MUL(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    tmp = Reg[rs_id]*Reg[rt_id]
    disassemble_ins = 'MUL' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    if (tmp <= pow(2, 31) - 1) and (tmp >= -pow(2, 31)): #在范围内
       Reg[rd_id]=tmp
    else:#不是32位，需要截断
        bin_tmp = bin(tmp)
        if bin_tmp[0] == '-':#为负数 符号位置1
            bin_tmp = '1' + bin_tmp[3:]
        else:#为正数 符号位置0
            bin_tmp = '0'+bin_tmp[2:]
        bin_tmp = com2ori(bin_tmp)#转为补码
        bin_tmp = bin_tmp[len(bin_tmp) - 32:len(bin_tmp)]#截断后32位
        tmp = com2dec(bin_tmp)#转为十进制
        Reg[rd_id] = tmp#赋值给寄存器
    return disassemble_ins
def act_AND(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id=int(instr[16:21],2)
    Reg[rd_id]=Reg[rs_id]&Reg[rt_id]
    disassemble_ins='AND'+' R'+str(rd_id)+', R'+str(rs_id)+', R'+str(rt_id)
    return disassemble_ins
def act_OR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    Reg[rd_id] = Reg[rs_id] | Reg[rt_id]
    disassemble_ins = 'OR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def act_XOR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    Reg[rd_id] = Reg[rs_id] ^ Reg[rt_id]
    disassemble_ins = 'XOR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def act_NOR(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    tmp_rs=Reg[rs_id]
    tmp_rt=Reg[rt_id]
    tmp_ans=""
    if tmp_rs==-pow(2,31):#如果rs为最小值
        tmp_rs="10000000000000000000000000000000"
    elif tmp_rt==-pow(2,31):#如果rt为最小值
        tmp_rt="10000000000000000000000000000000"
    else:
        tmp_rs=dec2ori(tmp_rs)#转二进制原码
        tmp_rt = dec2ori(tmp_rt)  # 转二进制原码
        tmp_rs=converTo32bit(tmp_rs)#32位对齐
        tmp_rt = converTo32bit(tmp_rt)  # 32位对齐
    for i in range(0,32):
        if not(tmp_rs[i]|tmp_rt[i]):#或非，如果都为0，那么为1
            tmp_ans+='1'
        else:
            tmp_ans+='0'
    if tmp_ans=="10000000000000000000000000000000":#结果如果为最小值
        Reg[rd_id] = -pow(2,31)
    else:
        Reg[rd_id]=com2dec(tmp_ans)
    disassemble_ins = 'NOR' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def act_SLT(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    rd_id = int(instr[16:21], 2)
    Reg[rd_id]=1 if Reg[rs_id]<Reg[rt_id] else 0
    disassemble_ins = 'SLT' + ' R' + str(rd_id) + ', R' + str(rs_id) + ', R' + str(rt_id)
    return disassemble_ins
def act_ADDI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = instr[16:32]
    tmp_imm=converTo32bit(tmp_imm)#转为32位
    tmp_imm=ori2dec(tmp_imm)#转为10进制
    tmp_rt=Reg[rs_id]+tmp_imm
    if tmp_rt>-pow(2,31) and tmp_rt<pow(2,31)-1:
        Reg[rt_id] = tmp_rt
    disassemble_ins = 'ADDI' +  ' R' + str(rt_id) + ', R' + str(rs_id)+ ', #'+str(tmp_imm)
    return disassemble_ins
def act_ANDI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = 16*'0'+instr[16:32]
    Reg[rt_id]=Reg[rs_id]&int(tmp_imm,2)
    disassemble_ins = 'ANDI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins
def act_ORI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = 16 * '0' + instr[16:32]
    Reg[rt_id] = Reg[rs_id] | int(tmp_imm, 2)
    disassemble_ins = 'ORI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins
def act_XORI(instr):
    rs_id = int(instr[6:11], 2)
    rt_id = int(instr[11:16], 2)
    tmp_imm = 16 * '0' + instr[16:32]
    Reg[rt_id] = Reg[rs_id] ^ int(tmp_imm, 2)
    disassemble_ins = 'XORI' + ' R' + str(rs_id) + ', R' + str(rt_id) + ', #' + str(tmp_imm)
    return disassemble_ins


class instruction:
    insAddr=0
    Category=0
    instr=np.zeros(32)
    inType=instr[0:2]
    opBin=instr[2:6]
    opDec=0
    opName=""
    disassemble_ins=""
#初始化
    def __init__(self,ID,instr):
        self.insAddr=PC
        self.instr=instr
        self.inType=instr[0:2]
        self.Category = 1 if self.inType == '01' else 2
        self.opBin=instr[2:6]
        self.opDec=int(self.opBin,2)
        self.opName = InsCat1[self.opDec] if self.Category == 1 else InsCat2[self.opDec]
        self.disassemble()

#输出
    def display(self):
        print(self.instr,self.insAddr,self.disassemble_ins)
    def getInfo(self):
        return(self.instr+'\t'+str(self.insAddr)+'\t'+self.disassemble_ins+'\n')

    def disassemble(self):
        if self.Category==1: #第一种指令
            if self.opName==InsCat1[0]: # J 跳转指令
                self.disassemble_ins=disassemble_J(self.instr,self.insAddr)
            elif self.opName==InsCat1[1]: # JR 跳转到寄存器中的地址指令
                self.disassemble_ins=disassemble_JR(self.instr)
            elif self.opName==InsCat1[2]:#'BEQ','BLTZ'
                self.disassemble_ins = disassemble_BEQ(self.instr)
            elif self.opName==InsCat1[3]:#'BLTZ'
                self.disassemble_ins = disassemble_BLTZ(self.instr)
            elif self.opName == InsCat1[4]:  # 'BGTZ'
                self.disassemble_ins = disassemble_BGTZ(self.instr)
            elif self.opName == InsCat1[5]:  # BREAK
                self.disassemble_ins = disassemble_BREAK(self.instr)
            elif self.opName == InsCat1[6]:  # SW
                self.disassemble_ins = disassemble_SW(self.instr)
            elif self.opName == InsCat1[7]:  # LW
                self.disassemble_ins = disassemble_LW(self.instr)
            elif self.opName == InsCat1[8]:  # SLL
                self.disassemble_ins = disassemble_SLL(self.instr)
            elif self.opName == InsCat1[9]:  # SRL
                self.disassemble_ins = disassemble_SRL(self.instr)
            elif self.opName == InsCat1[10]:  # SRA
                self.disassemble_ins = disassemble_SRA(self.instr)
            elif self.opName == InsCat1[11]:  # NOP
                self.disassemble_ins = disassemble_NOP(self.instr)
        else:
            if self.opName == InsCat2[0]:  # ADD 跳转指令
                self.disassemble_ins = disassemble_ADD(self.instr)
            elif self.opName == InsCat2[1]:  # SUB 跳转到寄存器中的地址指令
                self.disassemble_ins = disassemble_SUB(self.instr)
            elif self.opName == InsCat2[2]:  # 'MUL
                self.disassemble_ins = disassemble_MUL(self.instr)
            elif self.opName == InsCat2[3]:  # 'AND
                self.disassemble_ins = disassemble_AND(self.instr)
            elif self.opName == InsCat2[4]:  # 'OR
                self.disassemble_ins = disassemble_OR(self.instr)
            elif self.opName == InsCat2[5]:  # XOR
                self.disassemble_ins = disassemble_XOR(self.instr)
            elif self.opName == InsCat2[6]:  # NOR
                self.disassemble_ins = disassemble_NOR(self.instr)
            elif self.opName == InsCat2[7]:  # SLT
                self.disassemble_ins = disassemble_SLT(self.instr)
            elif self.opName == InsCat2[8]:  # ADDI
                self.disassemble_ins = disassemble_ADDI(self.instr)
            elif self.opName == InsCat2[9]:  # ANDI
                self.disassemble_ins = disassemble_ANDI(self.instr)
            elif self.opName == InsCat2[10]:  # ORI
                self.disassemble_ins = disassemble_ORI(self.instr)
            elif self.opName == InsCat2[11]:  # XORI
                self.disassemble_ins = disassemble_XORI(self.instr)

        file_dissembly.write("{}\t{}\t{}\n".format(self.instr,self.insAddr,self.disassemble_ins))
   #     print("{}\t{}\t{}\n".format(self.instr,self.insAddr,self.disassemble_ins))

    def actInstr(self):
        if self.Category == 1:  # 第一种指令
            if self.opName == InsCat1[0]:  # J 跳转指令
                self.disassemble_ins = act_J(self.instr)
            elif self.opName == InsCat1[1]:  # JR 跳转到寄存器中的地址指令
                self.disassemble_ins = act_JR(self.instr)
            elif self.opName == InsCat1[2]:  # 'BEQ','BLTZ'
                self.disassemble_ins = act_BEQ(self.instr)
            elif self.opName == InsCat1[3]:  # 'BLTZ'
                self.disassemble_ins = act_BLTZ(self.instr)
            elif self.opName == InsCat1[4]:  # 'BGTZ'
                self.disassemble_ins = act_BGTZ(self.instr)
            elif self.opName == InsCat1[5]:  # BREAK
                self.disassemble_ins = act_BREAK(self.instr)
            elif self.opName == InsCat1[6]:  # SW
                self.disassemble_ins = act_SW(self.instr)
            elif self.opName == InsCat1[7]:  # LW
                self.disassemble_ins = act_LW(self.instr)
            elif self.opName == InsCat1[8]:  # SLL
                self.disassemble_ins = act_SLL(self.instr)
            elif self.opName == InsCat1[9]:  # SRL
                self.disassemble_ins = act_SRL(self.instr)
            elif self.opName == InsCat1[10]:  # SRA
                self.disassemble_ins = act_SRA(self.instr)
            elif self.opName == InsCat1[11]:  # NOP
                self.disassemble_ins = act_NOP(self.instr)
        else:
            if self.opName == InsCat2[0]:  # ADD 跳转指令
                self.disassemble_ins = act_ADD(self.instr)
            elif self.opName == InsCat2[1]:  # SUB 跳转到寄存器中的地址指令
                self.disassemble_ins = act_SUB(self.instr)
            elif self.opName == InsCat2[2]:  # 'MUL
                self.disassemble_ins = act_MUL(self.instr)
            elif self.opName == InsCat2[3]:  # 'AND
                self.disassemble_ins = act_AND(self.instr)
            elif self.opName == InsCat2[4]:  # 'OR
                self.disassemble_ins = act_OR(self.instr)
            elif self.opName == InsCat2[5]:  # XOR
                self.disassemble_ins = act_XOR(self.instr)
            elif self.opName == InsCat2[6]:  # NOR
                self.disassemble_ins = act_NOR(self.instr)
            elif self.opName == InsCat2[7]:  # SLT
                self.disassemble_ins = act_SLT(self.instr)
            elif self.opName == InsCat2[8]:  # ADDI
                self.disassemble_ins = act_ADDI(self.instr)
            elif self.opName == InsCat2[9]:  # ANDI
                self.disassemble_ins = act_ANDI(self.instr)
            elif self.opName == InsCat2[10]:  # ORI
                self.disassemble_ins = act_ORI(self.instr)
            elif self.opName == InsCat2[11]:  # XORI
                self.disassemble_ins = act_XORI(self.instr)
        file_handle.write("--------------------\nCycle:{}\t{}\t{}\n".format(Cycle, self.insAddr, self.disassemble_ins))
     #   print("--------------------\nCycle:{} {} {}\n".format(Cycle, self.insAddr, self.disassemble_ins))
        printReg()
        printData()

# Process .txt instruction
with open("sample.txt","r") as f:
    instructions=f.readlines()
instr=[]
ifBreaked=0 #还没到数据区
DataAddr=0 #记录数据区开头地址
#读取指令

for i in range(0,len(instructions)):
    instructions[i] = instructions[i].strip('\n')
    if ifBreaked==1:#Break过了，进入数据区
        Imm.append(com2dec(instructions[i]))  # 存立即数
        ImmAddr.append(PC)#存立即数的地址
        file_dissembly.write("{}\t{}\t{}\n".format(instructions[i],PC,str(com2dec(instructions[i]))))
    else:
        if instructions[i][2:6] == '0101':  # 判断BREAK
            ifBreaked = 1#如果break了进入数据区
            DataAddr=PC+4 #存储数据区开头地址
        #没break就继续读指令
        instr_tmp = instruction(i, instructions[i])
        instr.append(instr_tmp)  # 存指令
       # instr[i].display()
    PC+=4#PC每次读完指令后加4


#下面是执行指令
PC=256
id_ins=int((PC-256)/4)
while(id_ins<len(instr)):#不break就继续执行
    Cycle+=1
    instr[id_ins].actInstr()#反汇编并执行
    PC+=4
    id_ins = int((PC - 256) / 4)#执行下一条指令

file_dissembly.close()
file_handle.close()

