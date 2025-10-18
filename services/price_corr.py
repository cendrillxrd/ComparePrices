import pandas as pd

from strategies.rules_strategies import RuleOldCollectionsStrategy
from workers.rules_applier import RulesApplier


def with_strategies(rules_strategy_cls: 'RulesStrategy'):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            self.rules_applier.set_strategy(rules_strategy_cls())
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


class PriceCorrService:
    def __init__(self):
        self.rules_applier = RulesApplier()

    @with_strategies(RuleOldCollectionsStrategy)
    def set_rule_old_collections(self, excel_df: pd.DataFrame) -> pd.DataFrame:
        excel_df = self.rules_applier.apply_rule(excel_df)
        return excel_df