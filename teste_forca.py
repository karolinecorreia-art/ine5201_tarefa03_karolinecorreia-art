# test_forca.py
import os
import tempfile
import unittest

import jogo_forca as jf


class TestLogica(unittest.TestCase):
    def test_remover_acentos(self):
        self.assertEqual(jf.remover_acentos("Ação Órfão"), "Acao Orfao")

    def test_atualizar_display(self):
        self.assertEqual(jf.atualizar_display("CASA", {"A"}), "_ A _ A")

    def test_verificar_vitoria(self):
        self.assertTrue(jf.verificar_vitoria("CASA", {"C", "A", "S"}))
        self.assertFalse(jf.verificar_vitoria("CASA", {"C", "A"}))

    def test_letras_ocultas_ordenadas(self):
        self.assertEqual(jf.letras_ocultas("CASA", {"A"}), ["C", "S"])

    def test_letras_erradas(self):
        self.assertEqual(jf.letras_erradas("CASA", {"Z", "A", "B"}), ["B", "Z"])

    def test_escolher_palavra_nao_repete(self):
        for _ in range(50):
            self.assertNotEqual(jf.escolher_palavra(["A", "B"], "A"), "A")

    def test_texto_estatisticas(self):
        self.assertIn("Aproveitamento: 75%", jf.texto_estatisticas(3, 1))
        self.assertIn("Aproveitamento: 0%", jf.texto_estatisticas(0, 0))


class TestArquivos(unittest.TestCase):
    def test_carregar_palavras_filtra(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "p.txt")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("Ação\ncasa\nCASA\n\nab1\n  teste  \n")
            self.assertEqual(jf.carregar_palavras(caminho),
                             ["ACAO", "CASA", "TESTE"])

    def test_estatisticas_ida_e_volta(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "s.json")
            self.assertTrue(jf.salvar_estatisticas(4, 2, caminho))
            self.assertEqual(jf.carregar_estatisticas(caminho), (4, 2))

    def test_estatisticas_invalidas_voltam_a_zero(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "s.json")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write('{"vitorias": "abc", "derrotas": -1}')
            self.assertEqual(jf.carregar_estatisticas(caminho), (0, 0))
            with open(caminho, "w", encoding="utf-8") as f:
                f.write("isso nao e json")
            self.assertEqual(jf.carregar_estatisticas(caminho), (0, 0))


if __name__ == "__main__":
    unittest.main()