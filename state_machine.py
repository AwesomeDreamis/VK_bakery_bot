class Machine:
    __state: str = None

    def get_state(self) -> str:
        """
        возвращает состояние машины
        :return: str
        """
        return self.__state

    def set_state(self, value: str):
        """
        устанавливает значение статуса
        :param state: значение
        :return: None
        """
        self.__state: str = value
