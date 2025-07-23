import pathlib
from Board import Board
from PieceFactory import PieceFactory
from Game import Game

def read_board_config(path: pathlib.Path):
    pieces_info = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid line in board.txt: {line}")
            # כאן אנחנו קוראים את סוג החייל (למשל 'QW'), לא ID ייחודי
            piece_type, r, c = parts[0], int(parts[1]), int(parts[2])
            pieces_info.append((piece_type, (r, c)))
    return pieces_info

def create_board(h=8, w=8) -> Board:
    from img import Img
    base_dir = pathlib.Path(__file__).parent
    board_img_path = base_dir.parent / "board.png"

    img = Img()
    img.read(str(board_img_path), size=(w * 64, h * 64))

    return Board(
        cell_H_pix=64,
        cell_W_pix=64,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=w,
        H_cells=h,
        img=img
    )

def main():
    base_dir = pathlib.Path(__file__).parent
    pieces_root = base_dir.parent / "pieces"
    board_txt = base_dir / "board.txt"

    board = create_board()
    piece_factory = PieceFactory(board, pieces_root)

    piece_positions = read_board_config(board_txt)
    game_pieces = []

    for piece_type, cell in piece_positions:
        # <<< הוספת לוגיקה ליצירת ID ייחודי
        # ניצור מזהה ייחודי על ידי שילוב סוג החייל והמיקום שלו
        # לדוגמה: חייל מסוג 'QW' במיקום (7, 4) יקבל את ה-ID: 'QW_7_4'
        unique_piece_id = f"{piece_type}_{cell[0]}_{cell[1]}"

        # נשתמש ב-ID הייחודי שיצרנו כדי ליצור את החייל
        piece = piece_factory.create_piece(unique_piece_id, cell)
        if piece is not None:
            game_pieces.append(piece)

    game = Game(game_pieces, board)
    game.run()

if __name__ == "__main__":
    main()