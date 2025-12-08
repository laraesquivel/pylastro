# --- 1. DEFINIÇÃO DE PERFIS (Setores e Produtos) ---

SETORES = {
    'Construção': [
        'Cimento', 'Tijolo', 'Vergalhão', 'Areia', 
        'Telha', 'Tinta', 'Madeira', 'Porta', 'Janela'
    ],
    'Tecnologia': [
        'Licença de Software', 'Notebook', 'Servidor', 'Cabo de Rede', 
        'Mouse', 'Teclado', 'Monitor', 'Roteador', 'SSD'
    ],
    'Alimentos': [
        'Farinha de Trigo', 'Açúcar', 'Óleo de Soja', 'Carne Bovina',
        'Arroz', 'Feijão', 'Leite', 'Café', 'Macarrão'
    ],
    'Automotivo': [
        'Pneu', 'Óleo Motor', 'Pastilha de Freio', 'Bateria',
        'Velas de Ignição', 'Amortecedor', 'Filtro de Ar', 'Correia Dentada'
    ],
    'Farmácia': [
        'Antibiótico', 'Analgésico', 'Fralda', 'Vitamina',
        'Xarope', 'Compressa', 'Soro Fisiológico', 'Protetor Solar'
    ],
    'Moda': [
        'Camiseta', 'Calça Jeans', 'Tênis', 'Vestido',
        'Jaqueta', 'Meias', 'Chapéu', 'Bolsa'
    ],
    'Esportes': [
        'Bola de Futebol', 'Raquete de Tênis', 'Tênis Esportivo', 'Bicicleta',
        'Luvas de Boxe', 'Tapete de Yoga', 'Corda de Pular', 'Halteres'
    ],
    'Móveis': [
        'Cadeira', 'Mesa', 'Sofá', 'Cama', 
        'Armário', 'Estante', 'Poltrona', 'Criado-mudo'
    ]
}

# --- 2. DEFINIÇÃO DE ESTADO ---

ESTADOS = ['SP', 'RJ', 'MG', 'RS', 'PE', 'BA', 'AC']

#--- 3.MATRIZ DE SUPRIMENTOS ---

SUPRIMENTOS = {
    'Construção': ['Construção', 'Tecnologia', 'Móveis'],  # construtoras compram materiais de construção, tecnologia para escritórios, móveis
    'Tecnologia': ['Tecnologia'],                           # empresas de tecnologia compram equipamentos e softwares
    'Alimentos': ['Alimentos', 'Tecnologia', 'Móveis'],    # supermercados compram alimentos, tecnologia e móveis
    'Automotivo': ['Automotivo', 'Tecnologia'],            # oficinas compram peças e equipamentos tecnológicos
    'Farmácia': ['Farmácia', 'Tecnologia', 'Móveis'],      # farmácias compram medicamentos, tecnologia para sistemas e móveis
    'Moda': ['Moda', 'Tecnologia', 'Móveis'],              # lojas de roupa compram produtos de moda, tecnologia e móveis
    'Esportes': ['Esportes', 'Tecnologia', 'Móveis'],      # lojas esportivas compram equipamentos, tecnologia e móveis
    'Móveis': ['Móveis', 'Tecnologia'],                    # lojas de móveis compram móveis e tecnologia para gestão
}

#---4. LABEL FRAUDES

LABEL_FRAUDES = ['Nenhuma','Duplicatas Falsas','Duplicatas Duplicadas','Endosso Indevido']