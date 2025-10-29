from abc import ABC, abstractmethod
from datetime import datetime


# === CLASSES ===

class Cliente:
    def __init__(self, nome, cpf, endereco, telefone, data_nascimento):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, endereco, telefone, data_nascimento):
        super().__init__(nome, cpf, endereco, telefone, data_nascimento)


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        if valor > self._saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([
            transacao for transacao in self.historico.transacoes
            if transacao["tipo"] == Saque.__name__
        ])

        if valor > self.limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False

        if numero_saques >= self.limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""\
Agência:\t{self.agencia}
C/C:\t\t{self.numero}
Titular:\t{self.cliente.nome}
"""


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


# === FUNÇÕES AUXILIARES ===

def buscar_conta_por_cpf(contas, cpf):
    for conta in contas:
        if conta.cliente.cpf == cpf:
            return conta
    return None


# === MENU INTERATIVO ===

def menu():
    clientes = []
    contas = []

    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1 - Cadastrar novo usuário")
        print("2 - Consultar saldo")
        print("3 - Realizar depósito")
        print("4 - Realizar saque")
        print("5 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\n=== Cadastro de Novo Usuário ===")
            nome = input("Informe o nome: ")
            cpf = input("Informe o CPF: ")
            endereco = input("Informe o endereço: ")
            telefone = input("Informe o telefone: ")
            data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")

            cliente = PessoaFisica(nome, cpf, endereco, telefone, data_nascimento)
            clientes.append(cliente)

            numero_conta = len(contas) + 1
            conta = ContaCorrente.nova_conta(cliente, numero_conta)
            cliente.adicionar_conta(conta)
            contas.append(conta)

            print("\n=== Usuário cadastrado com sucesso! ===")

        elif opcao == "2":
            cpf = input("Informe o CPF do cliente: ")
            conta = buscar_conta_por_cpf(contas, cpf)
            if conta:
                print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
            else:
                print("\n@@@ Conta não encontrada. @@@")

        elif opcao == "3":
            cpf = input("Informe o CPF do cliente: ")
            conta = buscar_conta_por_cpf(contas, cpf)
            if conta:
                valor = float(input("Informe o valor do depósito: "))
                transacao = Deposito(valor)
                conta.cliente.realizar_transacao(conta, transacao)
            else:
                print("\n@@@ Conta não encontrada. @@@")

        elif opcao == "4":
            cpf = input("Informe o CPF do cliente: ")
            conta = buscar_conta_por_cpf(contas, cpf)
            if conta:
                valor = float(input("Informe o valor do saque: "))
                transacao = Saque(valor)
                conta.cliente.realizar_transacao(conta, transacao)
            else:
                print("\n@@@ Conta não encontrada. @@@")

        elif opcao == "5":
            print("\nEncerrando o sistema. Até logo!")
            break

        else:
            print("\n@@@ Opção inválida. Tente novamente. @@@")

menu()
