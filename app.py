from flask import Flask, render_template, request, jsonify
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
# Em produção (Render) usa /data, em dev usa a pasta local
import os
_DATA_DIR = "/data" if os.path.isdir("/data") else os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(_DATA_DIR, "inspetores.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS unidades (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                desc TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS inspetores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                nome       TEXT NOT NULL,
                modalidade TEXT NOT NULL,
                status     TEXT NOT NULL DEFAULT 'FOLGA',
                funcao     TEXT DEFAULT '',
                matricula  TEXT DEFAULT '',
                empresa    TEXT DEFAULT 'GranServices',
                unidade_id INTEGER NOT NULL,
                FOREIGN KEY (unidade_id) REFERENCES unidades(id)
            );
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                inspetor_id   INTEGER NOT NULL,
                status_novo   TEXT NOT NULL,
                data          TEXT NOT NULL,
                data_embarque      TEXT DEFAULT '',
                data_previsao      TEXT DEFAULT '',
                data_retorno       TEXT DEFAULT '',
                dias_embarcados    INTEGER DEFAULT NULL,
                unidade_nome       TEXT DEFAULT '',
                coordenador   TEXT DEFAULT '',
                observacao    TEXT DEFAULT '',
                criado_em     TEXT NOT NULL,
                FOREIGN KEY (inspetor_id) REFERENCES inspetores(id)
            );
        """)

        # Migração silenciosa de colunas (para bancos já existentes)
        for col, default in [("data_embarque","''"), ("data_previsao","''"), ("data_retorno","''"), ("dias_embarcados","NULL"), ("unidade_nome","''")]:
            try:
                conn.execute(f"ALTER TABLE movimentacoes ADD COLUMN {col} TEXT DEFAULT {default}")
            except Exception:
                pass
        cur = conn.execute("SELECT COUNT(*) FROM unidades")
        if cur.fetchone()[0] == 0:
            _seed(conn)

def _seed(conn):
    seed_data = [
        ('DAVID FILANO PINTO', 'PINTURA', 'DISPONIVEL', 'INSPETOR DE PINTURA', 'FRI-01-10811', 'GranServices', 'BASE MACAE'),
        ('JOAO VICENTE SOARES ANDRADE', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA', 'FRI-01-11223', 'GranServices', '3R-7'),
        ('JOSE RAIMUNDO PEREIRA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DIMENSIONAL', 'FRI-01-11235', 'GranServices', 'BASE MACAE'),
        ('MAICON BARRETO MINGUTA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS', 'FRI-01-11435', 'GranServices', 'BASE MACAE'),
        ('MARVIM QUEIROZ TADIM', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA/LP ESCALADOR NI', 'FRI-01-11604', 'GranServices', 'PCH-2'),
        ('ALESSANDRO VEIGA DE OLIVEIRA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-11775', 'GranServices', 'BASE MACAE'),
        ('RAFAEL MOREIRA DA SILVA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR IF-TF/ABENDI N1', 'FRI-01-11820', 'GranServices', 'BASE MACAE'),
        ('THIAGO OLIVEIRA DA COSTA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR IF-TF/ABENDI N1', 'FRI-01-11896', 'GranServices', 'BASE MACAE'),
        ('MICHEL DE SOUZA FREITAS', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-11928', 'GranServices', 'P-43 INSUP'),
        ('CELIO DEODORO PINTO', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12107', 'GranServices', 'P-68 MIEE'),
        ('RAFAEL DA SILVA ANDRADE', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS', 'FRI-01-12142', 'GranServices', 'BASE MACAE'),
        ('MARCELO BRANT ROLAO', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12244', 'GranServices', 'PRA-1'),
        ('MARIANA SGOBERO BALBINO YAMAUCHI', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-12249', 'GranServices', 'BASE MACAE'),
        ('MICHEL DE OLIVEIRA RAMOS', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-01-12273', 'GranServices', 'PNA-2'),
        ('EDER FELICIO DOS SANTOS E SANTOS', 'ELETRICA', 'EMBARCADO', 'SUPERVISOR / INSPETOR DE ELETRICA', 'FRI-01-12283', 'GranServices', 'P-67 UMS'),
        ('CELSO SANTIAGO DE OLIVEIRA', 'ELETRICA', 'FOLGA', 'SUPERVISOR / INSPETOR DE ELETRICA', 'FRI-01-12305', 'GranServices', 'PNA-2'),
        ('CARLOS MAGNO GOMES RANGEL', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12331', 'GranServices', 'PNA-2'),
        ('WILDINER LUCIO DOS SANTOS', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12384', 'GranServices', 'P-67 UMS'),
        ('WERLLEN DA SILVA COSTA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR', 'FRI-01-12400', 'GranServices', 'P-71 MIEE'),
        ('GLADHISTON DE SOUZA MELLO', 'ME/EQUIPAMENTOS', 'AFASTADO', 'INSPETOR DE SOLDA/END/ EQUIPAMENTOS/ ME', 'FRI-01-12409', 'GranServices', 'P-67 UMS'),
        ('DOUGLAS PECANHA FERNANDES DE OLIVEIRA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12410', 'GranServices', 'P-48 INSUP'),
        ('SERGIO GUIMARAES', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-01-12419', 'GranServices', 'P-70 MIEE'),
        ('ENEIAS DE ALMEIDA MAGALHAES', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12452', 'GranServices', 'P-68 MIEE'),
        ('CASSIO GERALDO LEMES BATISTA DA SILVA', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-12479', 'GranServices', 'BASE MACAE'),
        ('GUILHERME DE OLIVEIRA PAIZANTE', 'SOLDA', 'PROGRAMADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12481', 'GranServices', 'MOP'),
        ('HELIO DE OLIVEIRA PRATES', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12498', 'GranServices', 'P-20'),
        ('LEVI DE CARVALHO FIGUEIREDO FRANCO', 'SOLDA', 'FOLGA', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-01-12583', 'GranServices', 'BASE MACAE'),
        ('JOAO LUIZ DA SILVA RAMOS', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DIMENSIONAL', 'FRI-01-12635', 'GranServices', 'BASE MACAE'),
        ('FLAVIO FRANCISCO FERREIRA DE SOUZA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-01-12725', 'GranServices', 'PNA-1'),
        ('PAULO ANDRE BARROSO NOGUEIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-12842', 'GranServices', 'P-08 | TRIDENT'),
        ('LUCAS COSTA ARAUJO', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-12869', 'GranServices', 'P-48 INSUP'),
        ('LINCON RIBEIRO THOMAZ', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-13004', 'GranServices', 'PNA-1'),
        ('THIAGO FELIPE DA SILVA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-13007', 'GranServices', 'BASE MACAE'),
        ('OSMAR GOMES DA SILVA JUNIOR', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-13036', 'GranServices', 'BASE MACAE'),
        ('WILSON RIBEIRO DOS SANTOS JUNIOR', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-13049', 'GranServices', 'BASE MACAE'),
        ('CARLOS EDUARDO DIAS', 'ELETRICA', 'FOLGA', 'INSPETOR DE ELETRICA', 'FRI-01-13079', 'GranServices', 'BASE MACAE'),
        ('VANDACTTES HAUM DACTTES', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1432', 'GranServices', 'BASE MACAE'),
        ('GUSTAVO MAGESTE ROCHA PEREIRA', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1466', 'GranServices', 'BASE MACAE'),
        ('DANILO ROBERTO MAISCH', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1541', 'GranServices', 'BASE MACAE'),
        ('DANIEL JOSE DA SILVA', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1635', 'GranServices', 'BASE MACAE'),
        ('ULDERSON DOS SANTOS GOMES', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1675', 'GranServices', 'BASE MACAE'),
        ('MARCIO ROGERIO SOUZA DE MORAES', 'ELETRICA', 'FOLGA', 'INSPETOR ELETRICA/INSTRUMENTACAO', 'FRI-01-1859', 'GranServices', 'BASE MACAE'),
        ('ALEX BRUGNI MAFRA NEY', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1861', 'GranServices', 'BASE MACAE'),
        ('VINICIUS BORGES DE SOUZA', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1975', 'GranServices', 'BASE MACAE'),
        ('FRANCISCO RAMOS SILVA JUNIOR', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-1981', 'GranServices', 'BASE MACAE'),
        ('ROBSON DE SOUZA', 'PINTURA', 'FÉRIAS', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-2014', 'GranServices', 'P-67 UMS'),
        ('MARCELO DA MOTA PACHECO', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-01-2077', 'GranServices', 'BASE MACAE'),
        ('ANDRE REIGO NIKLAUS', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-2208', 'GranServices', 'BASE MACAE'),
        ('JAIR JUNIOR ALMEIDA BATISTA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-2253', 'GranServices', 'PNA-1 UMS'),
        ('JOEL ALVES DE CARVALHO', 'SOLDA', 'PROGRAMADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-2590', 'GranServices', 'CDI IMR'),
        ('ELLEN NASCIMENTO XAVIER', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA', 'FRI-01-3436', 'GranServices', 'BASE MACAE'),
        ('VINICIUS TORRES GUEDES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-01-3511', 'GranServices', 'CDI IMR'),
        ('DIJEAN DOS SANTOS BARBOSA', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-01-3561', 'GranServices', 'P-09'),
        ('FABRICIA CRISTINA TRINDADE DO ROSARIO MONTEIRO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-3818', 'GranServices', 'BASE MACAE'),
        ('MARCO AURELIO MOCO DE AZEREDO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-4105', 'GranServices', 'PRA-1'),
        ('BRENO DA SILVA RIBEIRO', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-4119', 'GranServices', '3R-3'),
        ('BRUNO DE OLIVEIRA COSTA', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA/LP ESCALADOR NI', 'FRI-01-4156', 'GranServices', 'P-67 UMS'),
        ('ALEX COUTINHO DA SILVA ABREU', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS', 'FRI-01-4326', 'GranServices', 'BASE MACAE'),
        ('GIL CARLOS DE MOURA JUNIOR', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR IF-TF/ABENDI N2', 'FRI-01-4650', 'GranServices', 'BASE MACAE'),
        ('FLAVIO ALVES FERRAIS', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS / LPPM', 'FRI-01-4716', 'GranServices', 'BASE MACAE'),
        ('CLAUDIO RAMOS LACERDA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DIMENSIONAL', 'FRI-01-4722', 'GranServices', 'BASE MACAE'),
        ('LEANDRO FERREIRA MARINHO', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS', 'FRI-01-5002', 'GranServices', 'BASE MACAE'),
        ('LUIZ ANTONIO DA SILVA LOURENCO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-5014', 'GranServices', 'BASE MACAE'),
        ('EVANIO TRINDADE RODRIGUES FREITAS', 'ME/EQUIPAMENTOS', 'EMBARCADO', 'INSPETOR DE SOLDA/END/ EQUIPAMENTOS/ ME ESCALADOR NI', 'FRI-01-5175', 'GranServices', 'P-67 UMS'),
        ('MAYKON FELIX DE OLIVEIRA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-5430', 'GranServices', 'PNA-1'),
        ('YAN CALOMENI PEIXOTO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-5506', 'GranServices', 'BASE MACAE'),
        ('CHARLLES CORDEIRO NUNES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-5859', 'GranServices', 'PNA-1 UMS'),
        ('LAIO FALCAO GOMES ALVES', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR SOLDA/ENDS/ME', 'FRI-01-5863', 'GranServices', 'PCH-2'),
        ('MURILO LAMONICA DE AZEREDO', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-5866', 'GranServices', 'PNA-1 UMS'),
        ('RAFAEL DOS SANTOS SOUZA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-6209', 'GranServices', '3R-3'),
        ('PATRICK RIBEIRO PEREIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-01-6249', 'GranServices', 'BASE MACAE'),
        ('CARLO ALICIO FARIAS', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DIMENSIONAL', 'FRI-01-7191', 'GranServices', 'BASE MACAE'),
        ('CARLOS AUGUSTO BAHIA MARTINS', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-01-7236', 'GranServices', 'BASE MACAE'),
        ('FABIO GABRIEL DE ASSIS', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-750', 'GranServices', 'BASE MACAE'),
        ('LUCAS PEREIRA DE SOUZA', 'PINTURA', 'FOLGA', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8041', 'GranServices', 'P-08 TRIDENT'),
        ('FREDERICO DA SILVA BRAGA CAMPOS', 'PINTURA', 'EMBARCADO', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8064', 'GranServices', 'PPM-1 TRIDENT'),
        ('RODRIGO FELIX DE OLIVEIRA', 'PINTURA', 'FOLGA', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8066', 'GranServices', 'PCE-1 TRIDENT'),
        ('LISANEAS LAMOGLIA NEVES', 'SOLDA', 'EMBARCADO', 'COORDENADOR DE PRODUCAO', 'FRI-01-813', 'GranServices', 'CDI IMR'),
        ('JOEDSON SILVA PEREIRA', 'PINTURA', 'FOLGA', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8139', 'GranServices', 'PPM-1 TRIDENT'),
        ('LEONARDO ALVES NASCIMENTO', 'PINTURA', 'EMBARCADO', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8140', 'GranServices', 'PCE-1 TRIDENT'),
        ('BRUNO DE CASTRO SOUZA', 'PINTURA', 'FOLGA', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8262', 'GranServices', 'PCE-1 TRIDENT'),
        ('HEBER GOMES VIANNA', 'PINTURA', 'EMBARCADO', 'SUPERVISOR / INSPETOR DE PINTURA ESCALADOR', 'FRI-01-8321', 'GranServices', 'P-65 | TRIDENT'),
        ('ROBERTO ALVES', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-8371', 'GranServices', 'BASE MACAE'),
        ('MARCIANO SILVA BRANCO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-8407', 'GranServices', 'BASE MACAE'),
        ('LUANI DE VASCONCELOS', 'ME/EQUIPAMENTOS', 'DISPONIVEL', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-01-8841', 'GranServices', 'PGP-1'),
        ('FERNANDO RODRIGUES DE SOUZA JUNIOR', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-01-901', 'GranServices', 'BASE MACAE'),
        ('JOSE PEREIRA CALDEIRA NETTO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-01-9138', 'GranServices', 'CDI IMR'),
        ('JOAO MARCOS ABREU GONCALVES', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DIMENSIONAL/EQUIPAMENTOS', 'FRI-01-9969', 'GranServices', 'BASE MACAE'),
        ('FELIPE DE ALMEIDA ROCHA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-03-00271', 'GranServices', 'CDI IMR'),
        ('GABRIEL LEANDRO GONCALVES SANTANA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-03-00301', 'GranServices', 'PNA-1 UMS'),
        ('RODOLPHO CORREA MOLL', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-03-00304', 'GranServices', 'PNA-1 UMS'),
        ('DILEA MICHELSEN GONCALVES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR', 'FRI-03-00314', 'GranServices', 'CDI IMR'),
        ('WALDEVI FERREIRA LIMA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE SOLDA/END/ EQUIPAMENTOS/ ME ESCALADOR NI', 'FRI-03-00382', 'GranServices', 'BASE MACAE'),
        ('JOSE ALEXANDRE BRASIL CARDOSO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-05-00075', 'GranServices', 'BASE MACAE'),
        ('ELENILSON SANTOS LARANJEIRA', 'ME/EQUIPAMENTOS', 'PROGRAMADO', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00183', 'GranServices', 'MOP'),
        ('CLAUDEMIR ROSA GONCALVES', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00186', 'GranServices', 'P-57'),
        ('DOUGLAS DA COSTA GONCALVES', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00188', 'GranServices', 'PRA-1'),
        ('FABIO LUAN ROCHA DE OLIVEIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00244', 'GranServices', 'P-08 | TRIDENT'),
        ('TALLES DOS SANTOS NASCIMENTO', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-05-00247', 'GranServices', 'P-58'),
        ('LEONARDO SILVA PEREIRA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-05-00261', 'GranServices', 'P-58'),
        ('WAGNER VIGUINI MIRANDA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00271', 'GranServices', 'P-57'),
        ('BARTOLOMEU ASSENCAO DE SOUSA DIAS', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00302', 'GranServices', 'P-58'),
        ('MANUEL FELIPE SOLLEIRO DE AMORIM', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00332', 'GranServices', 'P-09'),
        ('HUDSON SANTANA DOS SANTOS', 'ME/EQUIPAMENTOS', 'EMBARCADO', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00348', 'GranServices', 'P-58'),
        ('RICARDO DA SILVA BATISTA', 'ME/EQUIPAMENTOS', 'EMBARCADO', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00349', 'GranServices', 'P-58'),
        ('RENATO PINHEIRO VICENTE', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00358', 'GranServices', 'P-58'),
        ('JOAO PAULO GONCALVES VIANA', 'PINTURA', 'FÉRIAS', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-05-00394', 'GranServices', 'P-68 MIEE'),
        ('SERGIO BOMFIM DOS SANTOS', 'ME/EQUIPAMENTOS', 'EMBARCADO', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00409', 'GranServices', 'PRA-1'),
        ('MATHEUS THIELMANN FONTES', 'ELETRICA', 'EMBARCADO', 'INSPETOR DE ELETRICA/INSTRUMENTACAO ESCALADOR NI', 'FRI-05-00412', 'GranServices', 'P-58'),
        ('NEY FRESSATO', 'ELETRICA', 'EMBARCADO', 'INSPETOR ELETRICA/INSTRUMENTACAO', 'FRI-05-00415', 'GranServices', 'P-58'),
        ('WELLITON AMARAL FERREIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-05-00425', 'GranServices', 'P-57'),
        ('FILLIPE GAMA REIS', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00427', 'GranServices', 'P-57'),
        ('GERALDO MARCELO TOFANI TOLEDO', 'ME/EQUIPAMENTOS', 'DISPONIVEL', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-00428', 'GranServices', 'PGP-1'),
        ('JOSE ANTONIO ALVES DA SILVA JUNIOR', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00458', 'GranServices', 'CDI IMR'),
        ('SANDRO SERAFIM GOMES', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-05-00509', 'GranServices', 'BASE MACAE'),
        ('DANIEL BARBOZA DE LIMA', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-05-00518', 'GranServices', 'BASE MACAE'),
        ('EDSON DOS SANTOS FARIA FILHO', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00520', 'GranServices', 'P-70-UMS'),
        ('MARLON MARQUES GENESIO DA SILVA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00589', 'GranServices', 'P-67 UMS'),
        ('MAURILIO DE LELIS HENRIQUES KNOP', 'ME/EQUIPAMENTOS', 'EMBARCADO', 'INSPETOR DE SOLDA/END/ EQUIPAMENTOS/ ME', 'FRI-05-00618', 'GranServices', 'P-68 MIEE'),
        ('ALUIZIO MELQUIZEDEQUE AUGUSTO SANTOS', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00681', 'GranServices', 'P-71 MIEE'),
        ('DANIEL FRANCISCO DE OLIVEIRA BOTELHO', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00691', 'GranServices', 'P-70 MIEE'),
        ('OLIMAR SEBASTIAO DE SIQUEIRA', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00715', 'GranServices', 'P-67 UMS'),
        ('WILSON DE OLIVEIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00786', 'GranServices', 'P-71 MIEE'),
        ('JOAO PAULO MONTEIRO JORDAO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00787', 'GranServices', 'P-67 UMS'),
        ('FERNANDO PINHO RAMOS JUNIOR', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00789', 'GranServices', 'P-67 UMS'),
        ('WEVERTON DE CARVALHO BELGA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00793', 'GranServices', 'PMLZ MIEE'),
        ('ADOLFO GUILHERME VOGEL GONCALVES', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00816', 'GranServices', 'PMXL MIEE'),
        ('IVO SANTOS DE JESUS', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00819', 'GranServices', 'PMLZ MIEE'),
        ('RONALDO GONCALVES BRITO', 'SOLDA', 'FÉRIAS', 'INSPETOR DE SOLDA', 'FRI-05-00846', 'GranServices', 'P-67 UMS'),
        ('JOAQUIM PESSANHA ROCHA', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00916', 'GranServices', 'PMLZ MIEE'),
        ('WESDRE RAMOS LEAL', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-00940', 'GranServices', 'PMXL MIEE'),
        ('ALEX COSTA MIRANDA', 'SOLDA', 'FOLGA', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00942', 'GranServices', 'PMLZ MIEE'),
        ('LUIZ ANTONIO VAZ DO NASCIMENTO', 'SOLDA', 'EMBARCADO', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-00947', 'GranServices', 'P-67 UMS'),
        ('JOSIAS FERREIRA DOS SANTOS', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00955', 'GranServices', 'PNA-1'),
        ('LUCAS FARIA HYPOLITO', 'PINTURA', 'DISPONIVEL', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00958', 'GranServices', 'PNA-1 UMS'),
        ('GEOVA FERREIRA SANTOS', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-00964', 'GranServices', 'P-67 UMS'),
        ('ALBERTO JUNIOR CARDOSO DA SILVA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01064', 'GranServices', 'PNA-1'),
        ('ZAQUEU ERICKSON DE ARAUJO CAMPOS', 'PINTURA', 'DISPONIVEL', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01518', 'GranServices', 'CDI IMR'),
        ('LEONARDO DE SOUZA NOGUEIRA', 'ME/EQUIPAMENTOS', 'FOLGA', 'INSPETOR DE EQUIPAMENTOS / MEDICAO DE ESPESSURA (ME) / END?s ESCALADOR', 'FRI-05-01535', 'GranServices', 'PNA-2'),
        ('GUTTEMBERG SANTOS SILVA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01546', 'GranServices', 'P-43 INSUP'),
        ('PATTRYCK LUGAO CORREIA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01576', 'GranServices', 'PNA-1'),
        ('MARCOS ROGERIO DA SILVA PRADO', 'SOLDA', 'AFASTADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01582', 'GranServices', 'P-20'),
        ('EDSON JOSE DE OLIVEIRA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01619', 'GranServices', 'P-71 MIEE'),
        ('JEFERSON LORENCO BRAGA', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01620', 'GranServices', 'PGP-1'),
        ('RICARDO DE AZEVEDO MACHADO', 'PINTURA', 'FÉRIAS', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01622', 'GranServices', 'P-48 INSUP'),
        ('RODRIGO SOUZA MENEZES', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01631', 'GranServices', 'PNA-1'),
        ('CARLOS IGOR MALAFAIA PINHEIRO', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01642', 'GranServices', 'P-37'),
        ('ALEX SANDRO LIMA DE AGUIAR', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01702', 'GranServices', 'P-65 | TRIDENT'),
        ('ALEXANDRE CHAGAS BARCELOS', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01732', 'GranServices', 'P-09'),
        ('IONIL GONCALVES DO ROSARIO JUNIOR', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-05-01733', 'GranServices', 'PNA-1'),
        ('ALTIEREZ RODRIGUES ALVES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01734', 'GranServices', 'FPSO ANNA NERY'),
        ('CARLOS PATRICIO RIBEIRO', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01737', 'GranServices', 'P-68 MIEE'),
        ('JOSILVIO DE SOUZA OLIVEIRA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA', 'FRI-05-01749', 'GranServices', 'P-33'),
        ('MARCOS HENRIQUE DO NASCIMENTO VALENTIM', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01779', 'GranServices', 'PNA-1'),
        ('DIONIS CARVALHO GOMES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01792', 'GranServices', 'P-65 | TRIDENT'),
        ('JOSE CARLOS DOS SANTOS COSTA', 'SOLDA', 'FOLGA', 'SUPERVISOR DE PRODUCAO/INSPETOR', 'FRI-05-01836', 'GranServices', 'P-71 MIEE'),
        ('VAGNER ALVES VENTURA', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01853', 'GranServices', 'PNA-2'),
        ('DIOGO DOCIO DE AQUINO RIBEIRO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01942', 'GranServices', 'P-43 INSUP'),
        ('RAFAEL DE LIMA RIBEIRO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-01950', 'GranServices', 'P-48 INSUP'),
        ('FRANCISCO MARCOS BARBOSA DO VALE', 'SOLDA', 'AFASTADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-01998', 'GranServices', 'PGP-1'),
        ('PIERRE PAULO GOMES DE CARVALHO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NIII', 'FRI-05-02166', 'GranServices', 'PMXL MIEE'),
        ('CHARLESTON DE SOUZA ALVES MENDES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02331', 'GranServices', 'PGP-1'),
        ('ILARIO LOURENCO', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02518', 'GranServices', 'PNA-1'),
        ('RODOLFO DOS SANTOS GOMES', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02527', 'GranServices', 'P-57'),
        ('VINICIUS DOS SANTOS GOMES', 'PINTURA', 'EMBARCADO', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02571', 'GranServices', 'P-70 MIEE'),
        ('ALISSON NASCIMENTO BOA MORTE', 'SOLDA', 'FOLGA', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-02625', 'GranServices', 'PGP-1'),
        ('ANDERSON CLEITON DOS SANTOS TEIXEIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02626', 'GranServices', 'P-20'),
        ('ALEX FREITAS REIS', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02634', 'GranServices', 'PMXL MIEE'),
        ('RICARDO NEVES SANTOS ROUGEMONT', 'SOLDA', 'EMBARCADO', 'INSPETOR DE SOLDA ESCALADOR NI', 'FRI-05-02668', 'GranServices', 'P-43 INSUP'),
        ('UESLEI DE ABREU NOGUEIRA', 'PINTURA', 'FOLGA', 'INSPETOR DE PINTURA ESCALADOR NI', 'FRI-05-02699', 'GranServices', 'PNA-2'),
        ('ALEXANDRE SILVEIRA DE CARVALHO', 'SOLDA', 'FOLGA', 'COORDENADOR DE PRODUCAO', 'FRI-07-00021', 'GranServices', 'BASE MACAE'),
    ]
    unidades_cache = {}
    for nome, mod, status, funcao, mat, empresa, unidade_nome in seed_data:
        if unidade_nome not in unidades_cache:
            cur = conn.execute("INSERT OR IGNORE INTO unidades (nome) VALUES (?)", (unidade_nome,))
            conn.execute("SELECT id FROM unidades WHERE nome=?", (unidade_nome,))
            uid = conn.execute("SELECT id FROM unidades WHERE nome=?", (unidade_nome,)).fetchone()[0]
            unidades_cache[unidade_nome] = uid
        uid = unidades_cache[unidade_nome]
        conn.execute(
            "INSERT INTO inspetores (nome, modalidade, status, funcao, matricula, empresa, unidade_id) VALUES (?,?,?,?,?,?,?)",
            (nome, mod, status, funcao, mat, empresa, uid)
        )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stats")
def api_stats():
    with get_db() as conn:
        total     = conn.execute("SELECT COUNT(*) FROM inspetores").fetchone()[0]
        embarcados= conn.execute("SELECT COUNT(*) FROM inspetores WHERE status='EMBARCADO'").fetchone()[0]
        folga     = conn.execute("SELECT COUNT(*) FROM inspetores WHERE status='FOLGA'").fetchone()[0]
        afastados = conn.execute("SELECT COUNT(*) FROM inspetores WHERE status IN ('AFASTADO','FÉRIAS')").fetchone()[0]
        unidades  = conn.execute("SELECT COUNT(*) FROM unidades").fetchone()[0]
    return jsonify(total=total, embarcados=embarcados, folga=folga, afastados=afastados, unidades=unidades)

@app.route("/api/unidades")
def api_unidades():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT u.id, u.nome, u.desc,
                   COUNT(i.id) as total,
                   SUM(CASE WHEN i.status='EMBARCADO' THEN 1 ELSE 0 END) as embarcados
            FROM unidades u
            LEFT JOIN inspetores i ON i.unidade_id = u.id
            GROUP BY u.id ORDER BY u.nome
        """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/unidades/<int:uid>/inspetores")
def api_unidade_inspetores(uid):
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, nome, modalidade, status, funcao, matricula, empresa
            FROM inspetores WHERE unidade_id=? ORDER BY nome
        """, (uid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/unidades", methods=["POST"])
def criar_unidade():
    d = request.json
    nome = d.get("nome","").strip().upper()
    desc = d.get("desc","").strip()
    if not nome:
        return jsonify(erro="Nome obrigatório"), 400
    try:
        with get_db() as conn:
            cur = conn.execute("INSERT INTO unidades (nome, desc) VALUES (?,?)", (nome, desc))
            uid = cur.lastrowid
        return jsonify(id=uid, nome=nome, desc=desc, total=0, embarcados=0), 201
    except sqlite3.IntegrityError:
        return jsonify(erro="Unidade já existe"), 409

@app.route("/api/unidades/<int:uid>", methods=["PUT"])
def editar_unidade(uid):
    d = request.json
    nome = d.get("nome","").strip().upper()
    desc = d.get("desc","").strip()
    if not nome:
        return jsonify(erro="Nome obrigatório"), 400
    try:
        with get_db() as conn:
            conn.execute("UPDATE unidades SET nome=?, desc=? WHERE id=?", (nome, desc, uid))
        return jsonify(ok=True)
    except sqlite3.IntegrityError:
        return jsonify(erro="Já existe uma unidade com esse nome"), 409

@app.route("/api/unidades/<int:uid>", methods=["DELETE"])
def excluir_unidade(uid):
    with get_db() as conn:
        conn.execute("DELETE FROM movimentacoes WHERE inspetor_id IN (SELECT id FROM inspetores WHERE unidade_id=?)", (uid,))
        conn.execute("DELETE FROM inspetores WHERE unidade_id=?", (uid,))
        conn.execute("DELETE FROM unidades WHERE id=?", (uid,))
    return jsonify(ok=True)

@app.route("/api/inspetores")
def api_inspetores():
    q     = request.args.get("q","").lower()
    fst   = request.args.get("status","")
    fmod  = request.args.get("modalidade","")
    funit = request.args.get("unidade_id","")
    femp  = request.args.get("empresa","")
    sql = """
        SELECT i.id, i.nome, i.modalidade, i.status, i.funcao, i.matricula, i.empresa,
               u.id as unidade_id, u.nome as unidade,
               (SELECT m.status_novo||'|'||m.coordenador||'|'||m.data
                FROM movimentacoes m WHERE m.inspetor_id=i.id
                ORDER BY m.criado_em DESC LIMIT 1) as ultimo_reg
        FROM inspetores i JOIN unidades u ON u.id = i.unidade_id WHERE 1=1
    """
    params = []
    if q:
        sql += " AND (LOWER(i.nome) LIKE ? OR LOWER(u.nome) LIKE ? OR LOWER(i.empresa) LIKE ? OR LOWER(i.matricula) LIKE ?)"
        params += [f"%{q}%"]*4
    if fst:  sql += " AND i.status=?";     params.append(fst)
    if fmod: sql += " AND i.modalidade=?"; params.append(fmod)
    if funit:sql += " AND u.id=?";         params.append(funit)
    if femp: sql += " AND i.empresa=?";    params.append(femp)
    sql += " ORDER BY u.nome, i.nome"
    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/inspetores", methods=["POST"])
def criar_inspetor():
    d = request.json
    nome    = d.get("nome","").strip().upper()
    mod     = d.get("modalidade","").strip()
    st      = d.get("status","FOLGA").strip()
    uid     = d.get("unidade_id")
    funcao  = d.get("funcao","").strip()
    mat     = d.get("matricula","").strip()
    empresa = d.get("empresa","").strip()
    if not nome or not mod or not uid:
        return jsonify(erro="Nome, modalidade e unidade são obrigatórios"), 400
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO inspetores (nome, modalidade, status, funcao, matricula, empresa, unidade_id) VALUES (?,?,?,?,?,?,?)",
            (nome, mod, st, funcao, mat, empresa, uid))
        iid = cur.lastrowid
    return jsonify(id=iid), 201

@app.route("/api/inspetores/<int:iid>", methods=["PUT"])
def editar_inspetor(iid):
    d = request.json
    nome    = d.get("nome","").strip().upper()
    mod     = d.get("modalidade","").strip()
    uid     = d.get("unidade_id")
    funcao  = d.get("funcao","").strip()
    mat     = d.get("matricula","").strip()
    empresa = d.get("empresa","").strip()
    if not nome or not mod or not uid:
        return jsonify(erro="Campos obrigatórios"), 400
    with get_db() as conn:
        conn.execute(
            "UPDATE inspetores SET nome=?, modalidade=?, unidade_id=?, funcao=?, matricula=?, empresa=? WHERE id=?",
            (nome, mod, uid, funcao, mat, empresa, iid))
    return jsonify(ok=True)

@app.route("/api/inspetores/<int:iid>", methods=["DELETE"])
def excluir_inspetor(iid):
    with get_db() as conn:
        conn.execute("DELETE FROM movimentacoes WHERE inspetor_id=?", (iid,))
        conn.execute("DELETE FROM inspetores WHERE id=?", (iid,))
    return jsonify(ok=True)

@app.route("/api/inspetores/<int:iid>/movimentacoes", methods=["GET"])
def historico(iid):
    from datetime import date
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM movimentacoes WHERE inspetor_id=? ORDER BY criado_em DESC LIMIT 50", (iid,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        # Usar dias salvos ou calcular
        if d.get("dias_embarcados") is None and d["status_novo"] == "EMBARCADO":
            try:
                de = d.get("data_embarque","") or d.get("data","")
                dr = d.get("data_retorno","")
                inicio = date.fromisoformat(de)
                fim    = date.fromisoformat(dr) if dr else date.today()
                d["dias_embarcados"] = (fim - inicio).days
            except Exception:
                pass
        result.append(d)
    return jsonify(result)

@app.route("/api/inspetores/<int:iid>/movimentacoes", methods=["POST"])
def registrar_movimentacao(iid):
    d    = request.json
    st   = d.get("status","").strip()
    dt   = d.get("data", datetime.today().strftime("%Y-%m-%d"))
    coord= d.get("coordenador","").strip()
    obs  = d.get("observacao","").strip()
    if not st:
        return jsonify(erro="Status obrigatório"), 400
    now = datetime.now().isoformat()
    # Calcular dias embarcados
    from datetime import date as ddate
    dias_emb = None
    manual = d.get("dias_embarcados_manual","")
    if manual and str(manual).isdigit():
        dias_emb = int(manual)
    elif st == "EMBARCADO":
        try:
            de = d.get("data_embarque","") or dt
            dr = d.get("data_retorno","")
            inicio = ddate.fromisoformat(de)
            fim    = ddate.fromisoformat(dr) if dr else ddate.today()
            dias_emb = (fim - inicio).days
        except Exception:
            pass
    with get_db() as conn:
        conn.execute("UPDATE inspetores SET status=? WHERE id=?", (st, iid))
        conn.execute(
            "INSERT INTO movimentacoes (inspetor_id,status_novo,data,data_embarque,data_previsao,data_retorno,dias_embarcados,unidade_nome,coordenador,observacao,criado_em) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (iid, st, dt, d.get("data_embarque",""), d.get("data_previsao",""), d.get("data_retorno",""), dias_emb, d.get("unidade_nome",""), coord, obs, now))
    return jsonify(ok=True)

@app.route("/exportar")
def exportar():
    import csv, io
    with get_db() as conn:
        rows = conn.execute("""
            SELECT i.matricula, i.nome, u.nome as unidade, i.modalidade, i.funcao, i.empresa, i.status
            FROM inspetores i JOIN unidades u ON u.id=i.unidade_id ORDER BY u.nome, i.nome
        """).fetchall()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Matrícula","Nome","Unidade","Modalidade","Função","Empresa","Status"])
    for r in rows:
        w.writerow([r["matricula"],r["nome"],r["unidade"],r["modalidade"],r["funcao"],r["empresa"],r["status"]])
    from flask import Response
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=inspetores.csv"})

if __name__ == "__main__":
    init_db()
    print("\n✅  App rodando em http://localhost:5000\n")
    app.run(debug=True, port=5000)
