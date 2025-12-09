from fastapi import APIRouter, HTTPException
from typing import Optional
from fastapi import Query


router = APIRouter(prefix="/mocks", tags=["Mocks"])
@router.get("/intituicoes")
def get_instituicoes(nome: Optional[str] = Query(default=None)):
    entidades = [
        {
            "nome_exato": "Consultoria e Gestão Empresarial Ltda",
            "tipo_instituicao": "Empresa de consultoria"
        },
        {
            "nome_exato": "M.S. Apoio Administrativo",
            "tipo_instituicao": "Empresa de serviços administrativos"
        },
        {
            "nome_exato": "João da Silva - CPF 123.456.789-00",
            "tipo_instituicao": "Pessoa física"
        },
        {
            "nome_exato": "Padaria e Confeitaria do Bairro",
            "tipo_instituicao": "Estabelecimento comercial (padaria)"
        },
        {
            "nome_exato": "Holding Patrimonial X",
            "tipo_instituicao": "Holding patrimonial"
        },
        {
            "nome_exato": "Associação de Moradores da Vila",
            "tipo_instituicao": "Associação civil"
        },
        {
            "nome_exato": "Lava Jato Rápido ME",
            "tipo_instituicao": "Microempresa (serviços de lavagem automotiva)"
        },
        {
            "nome_exato": "Maria Oliveira - CPF 987.654.321-00",
            "tipo_instituicao": "Pessoa física"
        },
        {
            "nome_exato": "J.P. Consultoria Individual",
            "tipo_instituicao": "Empresa de consultoria individual"
        },
        {
            "nome_exato": "Bar e Mercearia Central",
            "tipo_instituicao": "Comércio varejista"
        },
        {
            "nome_exato": "Banco do Brasil S.A.",
            "tipo_instituicao": "Instituição financeira (banco comercial)"
        },
        {
            "nome_exato": "Itaú Unibanco S.A.",
            "tipo_instituicao": "Instituição financeira (banco comercial)"
        },
        {
            "nome_exato": "Bradesco S.A.",
            "tipo_instituicao": "Instituição financeira (banco comercial)"
        },
        {
            "nome_exato": "Santander Brasil S.A.",
            "tipo_instituicao": "Instituição financeira (banco comercial)"
        },
        {
            "nome_exato": "Caixa Econômica Federal",
            "tipo_instituicao": "Instituição financeira (banco estatal)"
        },
        {
            "nome_exato": "BTG Pactual S.A.",
            "tipo_instituicao": "Instituição financeira (banco de investimentos)"
        },
        {
            "nome_exato": "Safra S.A.",
            "tipo_instituicao": "Instituição financeira (banco comercial)"
        },
        {
            "nome_exato": "Banco Inter S.A.",
            "tipo_instituicao": "Instituição financeira (banco digital)"
        }
    ]
    if nome is not None:
        entidades_filtradas = [e for e in entidades if e["nome_exato"] == nome]
        return {"entidades": entidades_filtradas}
    return {"entidades": entidades}
