import pandas as pd

def averageAndStd(data, monitorType):
    summary = pd.DataFrame({
        f'{monitorType}_mean': data.mean(axis=1),
        f'{monitorType}_std': data.std(axis=1)
    })

    summary[f'{monitorType}_2std'] = summary[f'{monitorType}_std']*2
    return summary
